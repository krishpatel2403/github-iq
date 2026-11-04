"""GitHub OAuth authentication routes.

Flow:
1. GET  /auth/github/login   -> backend creates a CSRF state cookie, redirects
                               browser to GitHub's OAuth authorize page.
2.      (user authorizes on GitHub)
3. GET  /auth/github/callback -> GitHub redirects here with ?code=..&state=..
                                Backend verifies state, exchanges code for an
                                access token, fetches the GitHub user profile,
                                encrypts + stores the token, creates/updates the
                                local user, sets a signed session cookie, then
                                redirects to the frontend dashboard.
4. GET  /auth/me              -> returns the current session user (cookie auth).
5. POST /auth/logout          -> clears the session cookie.
"""

from app.core.config import settings
from app.core.security import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE,
    sign_session,
    unsign_session,
)
from app.crud.user import upsert_user_and_connection
from app.db.session import get_db
from app.models.user import User
from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

router = APIRouter()

OAUTH_STATE_COOKIE = "githubiq_oauth_state"
GITHUB_SCOPE = "read:user repo"


def _oauth_client() -> AsyncOAuth2Client:
    """Build an Authlib OAuth2 client for GitHub."""
    return AsyncOAuth2Client(
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        redirect_uri=settings.GITHUB_CALLBACK_URL,
        scope=GITHUB_SCOPE,
    )


def _set_session_cookie(response: RedirectResponse, user_id: int) -> None:
    """Attach a signed, HttpOnly session cookie to the redirect response."""
    token = sign_session(user_id)
    is_secure = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE,
        path="/",
        httponly=True,
        secure=is_secure,
        samesite="lax",
    )


def _clear_session_cookie(response: RedirectResponse) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")


@router.get("/auth/github/login")
async def github_login(request: Request):
    """Start the GitHub OAuth flow.

    Generates a random state value, stores it in a signed cookie, and redirects
    the browser to GitHub's authorization page.
    """
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth is not configured. Set GITHUB_CLIENT_ID and "
            "GITHUB_CLIENT_SECRET in backend/.env",
        )

    client = _oauth_client()
    authorization_url, state = client.create_authorization_url(
        "https://github.com/login/oauth/authorize"
    )

    # Store state in a cookie so the callback can verify it (CSRF protection).
    is_secure = settings.ENVIRONMENT == "production"
    response = RedirectResponse(url=authorization_url, status_code=302)
    response.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=state,
        max_age=10 * 60,  # 10 minutes
        path="/api/v1/auth/github/callback",
        httponly=True,
        secure=is_secure,
        samesite="lax",
    )
    return response


@router.get("/auth/github/callback")
async def github_callback(
    request: Request,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Handle GitHub's OAuth callback.

    Verifies the CSRF state, exchanges the authorization code for an access
    token, fetches the GitHub user profile, persists the encrypted token, and
    establishes a session cookie before redirecting to the frontend.
    """
    # --- CSRF: verify state matches the cookie we set at /login -------------
    cookie_state = request.cookies.get(OAUTH_STATE_COOKIE)
    if not code or not state or state != cookie_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state or code.")

    # --- Exchange code for access token ------------------------------------
    client = _oauth_client()
    try:
        token = await client.fetch_token(
            "https://github.com/login/oauth/access_token",
            code=code,
        )
    except Exception as exc:  # noqa: BLE001 - surface a friendly error
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange OAuth code for token: {exc}",
        )

    access_token = token.get("access_token")
    scope = token.get("scope")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token returned.")

    # --- Fetch the authenticated user's profile from GitHub ----------------
    async with client:
        resp = await client.get("https://api.github.com/user")
        resp.raise_for_status()
        github_user = resp.json()

    # --- Persist user + encrypted token ------------------------------------
    user = upsert_user_and_connection(db, github_user, access_token, scope)

    # --- Establish session and redirect to frontend dashboard --------------
    response = RedirectResponse(url=settings.FRONTEND_URL, status_code=302)
    _set_session_cookie(response, user.id)
    # Clear the one-time state cookie.
    response.delete_cookie(key=OAUTH_STATE_COOKIE, path="/api/v1/auth/github/callback")
    return response


@router.get("/auth/me")
def auth_me(request: Request, db: Session = Depends(get_db)):
    """Return the currently signed-in user, or 401 if no valid session."""
    user = _get_current_user_from_request(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return {
        "id": user.id,
        "github_id": user.github_id,
        "username": user.username,
        "email": user.email,
        "avatar_url": user.avatar_url,
    }


@router.post("/auth/logout")
def auth_logout():
    """Clear the session cookie."""
    response = RedirectResponse(url=settings.FRONTEND_URL, status_code=302)
    _clear_session_cookie(response)
    return response


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_current_user_from_request(request: Request, db: Session) -> User | None:
    """Resolve the logged-in user from the signed session cookie."""
    session_cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_cookie:
        return None
    user_id = unsign_session(session_cookie)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id).first()
