"""User repository for database operations."""

import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with async database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address.

        Args:
            email: User email address

        Returns:
            User object if found, None otherwise
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User primary key

        Returns:
            User object if found, None otherwise
        """
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self) -> List[User]:
        """Get all users.

        Returns:
            List of all User objects (may be empty)
        """
        query = select(User).order_by(User.id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User object to create

        Returns:
            Created User object with id and timestamps
        """
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(
        self,
        user_id: int,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[User]:
        """Update user details.

        Args:
            user_id: User primary key
            full_name: New full name (if provided)
            email: New email (if provided)
            role: New role (if provided)
            is_active: New active status (if provided)

        Returns:
            Updated User object, None if user not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None

        if full_name is not None:
            user.full_name = full_name
        if email is not None:
            user.email = email
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def disable(self, user_id: int) -> Optional[User]:
        """Disable a user account.

        Args:
            user_id: User primary key

        Returns:
            Updated User object, None if user not found
        """
        return await self.update(user_id, is_active=False)

    async def enable(self, user_id: int) -> Optional[User]:
        """Enable a user account.

        Args:
            user_id: User primary key

        Returns:
            Updated User object, None if user not found
        """
        return await self.update(user_id, is_active=True)
