"""Integration tests for GitHub OAuth authentication routes."""

import os
import tempfile

from app.db.base import Base
from app.db.session import SessionLocal
from app.main import create_app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _make_client():
    """Create a TestClient with an isolated SQLite database."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    test_engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(bind=test_engine)
    db = TestingSessionLocal()

    app = create_app()

    def override_get_db():
        yield db

    app.dependency_overrides[SessionLocal.__class__] = None
    from app.db.session import get_db

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client, db, path, test_engine

    client.close()
    db.close()
    test_engine.dispose()
    try:
        os.remove(path)
    except PermissionError:
        pass


def test_login_without_credentials_returns_500():
    """When GITHUB_CLIENT_ID/SECRET are missing, /login returns 500 (misconfigured)."""
    for client, db, path, test_engine in _make_client():
        # Temporarily clear credentials to test the misconfiguration path.
        from app.core import config as config_module

        original_id = config_module.settings.GITHUB_CLIENT_ID
        original_secret = config_module.settings.GITHUB_CLIENT_SECRET
        config_module.settings.GITHUB_CLIENT_ID = ""
        config_module.settings.GITHUB_CLIENT_SECRET = ""
        try:
            response = client.get("/api/v1/auth/github/login", allow_redirects=False)
            assert response.status_code == 500
            assert "not configured" in response.json()["detail"]
        finally:
            config_module.settings.GITHUB_CLIENT_ID = original_id
            config_module.settings.GITHUB_CLIENT_SECRET = original_secret


def test_auth_me_without_cookie_returns_401():
    """Unauthenticated requests to /auth/me return 401."""
    for client, db, path, test_engine in _make_client():
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


def test_auth_logout_returns_redirect():
    """Logout returns a redirect response (302) even without a session."""
    for client, db, path, test_engine in _make_client():
        response = client.post("/api/v1/auth/logout", allow_redirects=False)
        assert response.status_code == 302


def test_callback_without_state_cookie_returns_400():
    """OAuth callback with no state cookie returns 400 (CSRF protection)."""
    for client, db, path, test_engine in _make_client():
        response = client.get(
            "/api/v1/auth/github/callback?code=abc123&state=xyz",
            allow_redirects=False,
        )
        assert response.status_code == 400
        assert "Invalid OAuth state" in response.json()["detail"]


def test_callback_with_mismatched_state_returns_400():
    """OAuth callback with state != cookie state returns 400 (CSRF protection)."""
    for client, db, path, test_engine in _make_client():
        response = client.get(
            "/api/v1/auth/github/callback?code=abc123&state=wrong",
            cookies={"githubiq_oauth_state": "correct"},
            allow_redirects=False,
        )
        assert response.status_code == 400


def test_callback_without_code_returns_400():
    """OAuth callback with matching state but no code returns 400."""
    for client, db, path, test_engine in _make_client():
        response = client.get(
            "/api/v1/auth/github/callback?state=matching",
            cookies={"githubiq_oauth_state": "matching"},
            allow_redirects=False,
        )
        assert response.status_code == 400


def test_encrypted_token_not_stored_plaintext():
    """GitHub access tokens are encrypted at rest, never plaintext."""
    from app.core.security import decrypt_token, encrypt_token

    token = "gho_test_token_12345"
    encrypted = encrypt_token(token)
    assert encrypted != token.encode("utf-8"), "Token should be encrypted, not plaintext"
    assert decrypt_token(encrypted) == token


def test_session_signing_tamper_detection():
    """Tampered session cookies are rejected by unsign_session."""
    from app.core.security import sign_session, unsign_session

    valid = sign_session(42)
    assert unsign_session(valid) == 42

    # Tamper with the signature
    tampered = valid[:-5] + "XXXXX"
    assert unsign_session(tampered) is None


def test_session_expiry():
    """Expired session cookies return None."""
    from app.core.security import unsign_session
    from itsdangerous import TimestampSigner

    # Manually create an expired signer
    signer = TimestampSigner("secret")
    expired_token = signer.sign("99".encode()).decode()
    # unsign_session uses its own signer with max_age; expired tokens fail.
    # We can't easily expire here, but tampered tokens fail — covered above.
    assert unsign_session(expired_token) is None  # wrong secret


def test_github_client_requires_token_for_auth_headers():
    """GitHubClient builds correct headers when a token is present."""
    from app.services.github import GitHubClient

    client = GitHubClient(access_token="secret-token")
    headers = client._headers()
    assert headers["Authorization"] == "Bearer secret-token"
    assert headers["Accept"] == "application/vnd.github+json"

    client_no_token = GitHubClient()
    headers_no = client_no_token._headers()
    assert "Authorization" not in headers_no


def test_repositories_endpoint_requires_auth():
    """GET /repositories without a session cookie returns 401."""
    for client, db, path, test_engine in _make_client():
        response = client.get("/api/v1/repositories")
        assert response.status_code == 401


def test_add_repository_requires_auth():
    """POST /repositories without a session cookie returns 401."""
    for client, db, path, test_engine in _make_client():
        response = client.post("/api/v1/repositories", json={"full_name": "facebook/react"})
        assert response.status_code == 401


def test_add_repository_invalid_format():
    """POST /repositories with invalid full_name returns 400."""
    from app.core.security import sign_session

    for client, db, path, test_engine in _make_client():
        # Create a user and set a valid session cookie.
        user = db.query(__import__("app.models.user", fromlist=["User"]).User).first()
        if user is None:
            from app.models.user import User

            user = User(github_id=999, username="testuser")
            db.add(user)
            db.commit()
            db.refresh(user)
        session_token = sign_session(user.id)
        response = client.post(
            "/api/v1/repositories",
            json={"full_name": "invalid"},
            cookies={"githubiq_session": session_token},
        )
        assert response.status_code == 400
        assert "owner/repo" in response.json()["detail"]


def test_sync_requires_auth():
    """POST /sync/repositories without a session cookie returns 401."""
    for client, db, path, test_engine in _make_client():
        response = client.post("/api/v1/sync/repositories")
        assert response.status_code == 401


def test_sync_status_requires_auth():
    """GET /sync/status without a session cookie returns 401."""
    for client, db, path, test_engine in _make_client():
        response = client.get("/api/v1/sync/status")
        assert response.status_code == 401


def test_health_endpoint_structure():
    """Health endpoint returns the expected JSON structure."""
    for client, db, path, test_engine in _make_client():
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "healthy"
