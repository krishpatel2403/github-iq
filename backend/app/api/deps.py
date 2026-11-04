from typing import Annotated

from app.core.security import SESSION_COOKIE_NAME, unsign_session
from app.db.session import get_db
from app.models.user import User
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

DbDep = Annotated[Session, Depends(get_db)]


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Return the current user from the session cookie, or None."""
    session_cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_cookie:
        return None
    user_id = unsign_session(session_cookie)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id).first()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Return the current user, or raise 401 if not authenticated."""
    user = get_current_user_optional(request, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
