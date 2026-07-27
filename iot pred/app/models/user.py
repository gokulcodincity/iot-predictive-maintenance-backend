"""User model for authentication and user management."""

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import UserRole
from app.models.base import BaseModel


class User(BaseModel):
    """User model for storing user information."""

    __tablename__ = "users"
    __allow_unmapped__ = True

    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
