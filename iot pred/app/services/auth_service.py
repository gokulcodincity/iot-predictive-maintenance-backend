"""Authentication service for user authentication and token generation."""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service for authenticating users and generating JWT tokens."""

    def __init__(self, db: AsyncSession):
        """Initialize authentication service with async database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db
        self.user_repository = UserRepository(db)

    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[dict]:
        """Authenticate user by username and password.

        Verifies user credentials and generates JWT access token if valid.
        Returns None if user not found or password incorrect (fails safely).

        Args:
            username: User's username (unique identifier)
            password: User's plaintext password (never stored)

        Returns:
            Dictionary with access token if authentication succeeds:
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIs...",
                    "token_type": "bearer"
                }

            None if user not found or password invalid

        Example:
            >>> result = await auth_service.authenticate_user("operator_001", "secure_password")
            >>> if result:
            ...     token = result["access_token"]
            ...     # Use token in Authorization header
            ...else:
            ...     # Invalid credentials
            ...     pass
        """
        try:
            # Step 1: Find user by username
            logger.debug(f"Authenticating user: {username}")
            user = await self.user_repository.get_by_username(username)

            if not user:
                logger.warning(f"Authentication failed: user {username} not found")
                return None

            # Step 2: Verify password using timing-safe comparison
            if not verify_password(password, user.password_hash):
                logger.warning(f"Authentication failed: invalid password for {username}")
                return None

            # Step 3: Create JWT access token
            access_token = create_access_token({"sub": user.username})

            logger.info(f"User {username} authenticated successfully")

            # Step 4: Return token response
            return {
                "access_token": access_token,
                "token_type": "bearer",
            }

        except Exception as e:
            logger.error(f"Authentication error for {username}: {str(e)}")
            return None
