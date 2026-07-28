"""Security utilities for password hashing and JWT token management."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing configuration (bcrypt with auto-scheme detection)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Converts plaintext password to irreversible hash using bcrypt algorithm.
    Used when creating new user accounts or changing passwords.

    Args:
        password: Plaintext password to hash

    Returns:
        Bcrypt hash string suitable for database storage

    Example:
        >>> hashed = hash_password("user_password_123")
        >>> len(hashed) > 20  # Bcrypt hashes are ~60 characters
        True
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash.

    Safely compares plaintext password to stored hash using timing-safe comparison.
    Used during login to authenticate users.

    Args:
        plain_password: Plaintext password from login request
        hashed_password: Bcrypt hash from database

    Returns:
        True if password matches hash, False otherwise

    Example:
        >>> hashed = hash_password("secret")
        >>> verify_password("secret", hashed)
        True
        >>> verify_password("wrong", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create JWT access token with standard claims.

    Generates a signed JWT token containing user claims and expiration.
    Token claims include:
        - sub: Subject (typically user ID or username)
        - iat: Issued At (token creation timestamp)
        - exp: Expiration (token expiration timestamp)

    Args:
        data: Dictionary with user claims, should include "sub" key

    Returns:
        Encoded JWT token string

    Raises:
        KeyError: If SECRET_KEY not configured
        Exception: If JWT encoding fails

    Example:
        >>> token = create_access_token({"sub": "user_id_123"})
        >>> len(token) > 50  # JWT tokens are typically >100 chars
        True
    """
    token_data = data.copy()

    # Calculate expiration time
    expire_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire_time = datetime.now(timezone.utc) + expire_delta

    # Add JWT standard claims
    token_data.update({
        "exp": expire_time,  # Expiration time
        "iat": datetime.now(timezone.utc),  # Issued at time
    })

    # Encode and sign token
    token = jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return token


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate JWT access token.

    Verifies JWT signature and expiration, returns payload if valid.
    Used to extract user information from token in protected endpoints.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary with token payload (including sub, exp, iat) if valid
        None if token is invalid, expired, or tampered

    Example:
        >>> token = create_access_token({"sub": "user_123"})
        >>> payload = decode_access_token(token)
        >>> payload["sub"]
        "user_123"
        >>> decode_access_token("invalid.token.here") is None
        True
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        # Invalid signature, expired, malformed, or other JWT error
        return None
