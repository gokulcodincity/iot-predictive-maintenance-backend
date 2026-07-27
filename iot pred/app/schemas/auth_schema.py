"""Authentication schemas for login and token management."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema for login request."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    sub: str
    exp: int
