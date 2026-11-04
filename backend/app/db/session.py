"""Database engine and session factory."""

from pathlib import Path

from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_url = settings.DATABASE_URL

# Ensure the parent directory exists for file-based SQLite databases so the
# app can start even when the data folder has not been created yet.
if database_url.startswith("sqlite:///"):
    db_path = Path(database_url[len("sqlite:///") :])
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

# SQLite needs check_same_thread=False because FastAPI may use multiple threads.
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yield a SQLAlchemy session and close it when done (FastAPI dependency)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
