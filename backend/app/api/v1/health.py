from app.db.session import engine
from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter()


@router.get("/health")
def health():
    """Health check: verifies the API is up and can reach the database."""
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {exc}"

    return {"status": "ok", "database": db_status}
