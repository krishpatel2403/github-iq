"""Application configuration using Pydantic Settings.

Reads from backend/.env and environment variables.
Never hard-code secrets here — they come from the environment.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "GitHubIQ"
    ENVIRONMENT: str = "development"
    BACKEND_PORT: int = 8000
    SECRET_KEY: str = "change-me-in-production"

    # --- Database (SQLite for MVP; switch to Postgres later) ---
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # --- GitHub OAuth App ---
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_CALLBACK_URL: str = "http://localhost:8000/api/v1/auth/github/callback"

    # --- Frontend URL (for post-auth redirects) ---
    FRONTEND_URL: str = "http://localhost:5173"

    # --- Encryption / sessions ---
    GITHUB_TOKEN_ENCRYPTION_KEY: str = ""
    SESSION_SECRET_KEY: str = ""

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"


settings = Settings()
