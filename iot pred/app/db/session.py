"""Database session management - sync wrapper for backwards compatibility."""

from sqlalchemy.orm import Session

from app.db.database import Base

# For backwards compatibility with sync code
# In production, migrate all endpoints to use async get_async_session from database.py
SessionLocal = None  # Placeholder for sync sessions

def get_db() -> Session:
    """Get database session for sync endpoints (deprecated - use get_async_session).

    This is a compatibility layer. New code should use get_async_session from database.py.
    """
    raise NotImplementedError(
        "Sync get_db() is deprecated. Use get_async_session from app.db.database instead."
    )
