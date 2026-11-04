"""FastAPI application factory.

Wires together configuration, middleware, database, and API routers.
Run with:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all models so SQLAlchemy registers the tables (needed by Alembic too).
import app.models  # noqa: F401
from app.api.v1 import auth, health, repositories, sync
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.utils.logger import setup_logging

setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version="0.1.0")

    # CORS — restrict to the frontend origin. Never "*" in production.
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(repositories.router, prefix="/api/v1")
    app.include_router(sync.router, prefix="/api/v1")

    @app.on_event("startup")
    def on_startup():
        # Create tables on startup (dev). Alembic manages migrations in production.
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
