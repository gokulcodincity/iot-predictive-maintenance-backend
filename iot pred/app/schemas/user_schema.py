"""User schemas for request and response validation."""

from pydantic import BaseModel, ConfigDict

from app.core.constants import UserRole


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    full_name: str
    email: str
    password: str
    role: UserRole


class UserResponse(BaseModel):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
