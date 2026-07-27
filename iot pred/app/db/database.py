"""Database configuration and SQLAlchemy setup."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
