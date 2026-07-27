"""Database session management."""

from typing import Generator

from app.db.database import SessionLocal


def get_db() -> Generator:
    """Get a database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
