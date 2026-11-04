"""CRUD operations for users and GitHub connections."""

from sqlalchemy.orm import Session

from app.core.security import encrypt_token
from app.models.connection import GitHubConnection
from app.models.user import User


def get_user_by_github_id(db: Session, github_id: int) -> User | None:
    """Fetch a user by their GitHub user id."""
    return db.query(User).filter(User.github_id == github_id).first()


def upsert_user_and_connection(
    db: Session,
    github_user: dict,
    access_token: str,
    scope: str | None,
) -> User:
    """Create or update a user and their encrypted GitHub connection.

    Returns the User instance (committed and refreshed).
    """
    github_id = github_user["id"]
    encrypted = encrypt_token(access_token)

    user = get_user_by_github_id(db, github_id)

    if user:
        # Update profile fields in case they changed on GitHub.
        user.username = github_user.get("login", user.username)
        user.email = github_user.get("email")
        user.avatar_url = github_user.get("avatar_url")
        conn = db.query(GitHubConnection).filter(GitHubConnection.user_id == user.id).first()
        if conn:
            conn.encrypted_access_token = encrypted
            conn.token_scope = scope
        else:
            conn = GitHubConnection(
                user_id=user.id,
                encrypted_access_token=encrypted,
                token_scope=scope,
            )
            db.add(conn)
    else:
        user = User(
            github_id=github_id,
            username=github_user.get("login", ""),
            email=github_user.get("email"),
            avatar_url=github_user.get("avatar_url"),
        )
        db.add(user)
        db.flush()  # Assign user.id before creating the connection.
        conn = GitHubConnection(
            user_id=user.id,
            encrypted_access_token=encrypted,
            token_scope=scope,
        )
        db.add(conn)

    db.commit()
    db.refresh(user)
    return user
