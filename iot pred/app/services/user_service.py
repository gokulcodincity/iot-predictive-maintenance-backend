"""User service for user management business logic."""

import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db
        self.repository = UserRepository(db)

    async def get_all_users(self) -> List[UserResponse]:
        """Get all users.

        Returns:
            List of UserResponse objects

        Raises:
            Exception: If database operation fails
        """
        try:
            users = await self.repository.get_all()
            logger.info(f"Retrieved {len(users)} users")
            return [UserResponse.model_validate(user) for user in users]
        except Exception as e:
            logger.error(f"Error retrieving all users: {str(e)}")
            raise

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID.

        Args:
            user_id: User primary key

        Returns:
            UserResponse if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                return None

            logger.info(f"Retrieved user {user_id}")
            return UserResponse.model_validate(user)
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email.

        Args:
            email: User email address

        Returns:
            UserResponse if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            user = await self.repository.get_by_email(email)
            if not user:
                logger.warning(f"User with email {email} not found")
                return None

            return UserResponse.model_validate(user)
        except Exception as e:
            logger.error(f"Error retrieving user by email: {str(e)}")
            raise

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user.

        Args:
            user_data: UserCreate schema with user details

        Returns:
            Created UserResponse object

        Raises:
            ValueError: If email already exists
            Exception: If database operation fails
        """
        try:
            # Check if email already exists
            existing_user = await self.repository.get_by_email(user_data.email)
            if existing_user:
                logger.warning(f"User creation failed: email {user_data.email} already exists")
                raise ValueError(f"Email {user_data.email} already exists")

            # Create new user with hashed password
            user = User(
                full_name=user_data.full_name,
                email=user_data.email,
                password=hash_password(user_data.password),
                role=user_data.role,
                is_active=True,
            )

            created_user = await self.repository.create(user)
            logger.info(f"User {created_user.id} created: {created_user.email}")
            return UserResponse.model_validate(created_user)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    async def update_user(
        self, user_id: int, update_data: UserUpdate
    ) -> Optional[UserResponse]:
        """Update user details.

        Args:
            user_id: User primary key
            update_data: UserUpdate schema with fields to update

        Returns:
            Updated UserResponse if successful, None if user not found

        Raises:
            ValueError: If email is taken by another user
            Exception: If database operation fails
        """
        try:
            # Get current user
            current_user = await self.repository.get_by_id(user_id)
            if not current_user:
                logger.warning(f"User {user_id} not found for update")
                return None

            # Check if email is being changed to existing email
            if update_data.email and update_data.email != current_user.email:
                existing_user = await self.repository.get_by_email(update_data.email)
                if existing_user:
                    logger.warning(f"Update failed: email {update_data.email} already in use")
                    raise ValueError(f"Email {update_data.email} already in use")

            # Hash password if provided
            password = None
            if update_data.password:
                password = hash_password(update_data.password)

            # Update user
            updated_user = await self.repository.update(
                user_id,
                full_name=update_data.full_name,
                email=update_data.email,
                role=update_data.role,
                is_active=update_data.is_active,
            )

            # Update password separately if provided (don't include in update() call)
            if password:
                updated_user.password = password
                await self.db.commit()
                await self.db.refresh(updated_user)

            logger.info(f"User {user_id} updated")
            return UserResponse.model_validate(updated_user)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise

    async def assign_role(self, user_id: int, role: UserRole) -> Optional[UserResponse]:
        """Assign a role to a user.

        Args:
            user_id: User primary key
            role: New UserRole to assign

        Returns:
            Updated UserResponse if successful, None if user not found

        Raises:
            Exception: If database operation fails
        """
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for role assignment")
                return None

            old_role = user.role
            updated_user = await self.repository.update(user_id, role=role)

            logger.info(f"User {user_id} role changed: {old_role.value} → {role.value}")
            return UserResponse.model_validate(updated_user)

        except Exception as e:
            logger.error(f"Error assigning role to user {user_id}: {str(e)}")
            raise

    async def disable_user(self, user_id: int) -> Optional[UserResponse]:
        """Disable a user account.

        Args:
            user_id: User primary key

        Returns:
            Updated UserResponse if successful, None if user not found

        Raises:
            Exception: If database operation fails
        """
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for disabling")
                return None

            updated_user = await self.repository.disable(user_id)
            logger.info(f"User {user_id} disabled")
            return UserResponse.model_validate(updated_user)

        except Exception as e:
            logger.error(f"Error disabling user {user_id}: {str(e)}")
            raise

    async def enable_user(self, user_id: int) -> Optional[UserResponse]:
        """Enable a user account.

        Args:
            user_id: User primary key

        Returns:
            Updated UserResponse if successful, None if user not found

        Raises:
            Exception: If database operation fails
        """
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found for enabling")
                return None

            updated_user = await self.repository.enable(user_id)
            logger.info(f"User {user_id} enabled")
            return UserResponse.model_validate(updated_user)

        except Exception as e:
            logger.error(f"Error enabling user {user_id}: {str(e)}")
            raise
