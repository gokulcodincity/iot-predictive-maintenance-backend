"""Base model class with common columns."""

from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import mapped_column

from app.db.database import Base


class BaseModel(Base):
    """Abstract base model with common columns for all models."""

    __abstract__ = True

    id: int = mapped_column(Integer, primary_key=True, index=True)
    created_at: datetime = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: datetime = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
