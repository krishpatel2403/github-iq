"""Security helpers: Fernet encryption for GitHub tokens, signed session cookies.

- GitHub access tokens are encrypted at rest with Fernet (symmetric encryption).
- Session cookies are signed with itsdangerous so the client cannot tamper with them.
"""

from app.core.config import settings
from cryptography.fernet import Fernet
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner

# --- Fernet (token encryption) ------------------------------------------------
_fernet_key_raw = settings.GITHUB_TOKEN_ENCRYPTION_KEY
try:
    _fernet = Fernet(
        _fernet_key_raw.encode("utf-8") if isinstance(_fernet_key_raw, str) else _fernet_key_raw
    )
except (ValueError, TypeError):
    # Placeholder or invalid key — generate a dev key so the app starts.
    # In production, set a real key via: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # noqa: E501
    _fernet_key_raw = Fernet.generate_key().decode()
    _fernet = Fernet(_fernet_key_raw.encode("utf-8"))


def encrypt_token(token: str) -> bytes:
    """Encrypt a GitHub access token for storage in the database."""
    return _fernet.encrypt(token.encode("utf-8"))


def decrypt_token(encrypted: bytes) -> str:
    """Decrypt a stored GitHub access token back to plaintext."""
    return _fernet.decrypt(encrypted).decode("utf-8")


# --- Signed session cookie ----------------------------------------------------
_signer = TimestampSigner(settings.SESSION_SECRET_KEY or "dev-secret-change-me")
SESSION_COOKIE_NAME = "githubiq_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


def sign_session(user_id: int) -> str:
    """Create a signed session token string for the given user id."""
    return _signer.sign(str(user_id).encode("utf-8")).decode("utf-8")


def unsign_session(signed: str) -> int | None:
    """Verify a signed session token and return the user id, or None if invalid/expired."""
    try:
        user_id_str = _signer.unsign(signed.encode("utf-8"), max_age=SESSION_MAX_AGE).decode(
            "utf-8"
        )
        return int(user_id_str)
    except (BadSignature, SignatureExpired, ValueError):
        return None
