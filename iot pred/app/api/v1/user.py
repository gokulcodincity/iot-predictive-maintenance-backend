"""User API endpoints with role-based access control."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorization import Permission
from app.core.constants import UserRole
from app.db.database import get_async_session
from app.dependencies.authorization import require_permission
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
):
    """Get all users.

    Requires: MANAGE_USERS permission (Admin only)

    Returns:
        HTTP 200 with list of users (may be empty)
        HTTP 403 if unauthorized
    """
    try:
        service = UserService(db)
        users = await service.get_all_users()
        logger.info(f"Listed {len(users)} users by admin {current_user.id}")
        return users
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
):
    """Get user by ID.

    Requires: MANAGE_USERS permission (Admin only)

    Args:
        user_id: User primary key

    Returns:
        HTTP 200 with user details
        HTTP 403 if unauthorized
        HTTP 404 if user not found
    """
    try:
        service = UserService(db)
        user = await service.get_user_by_id(user_id)

        if not user:
            logger.warning(f"User {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        logger.info(f"Retrieved user {user_id} by admin {current_user.id}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user",
        )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
):
    """Create a new user.

    Requires: MANAGE_USERS permission (Admin only)

    Args:
        user_data: User creation data (email, full_name, password, role)

    Returns:
        HTTP 201 with created user
        HTTP 403 if unauthorized
        HTTP 409 if email already exists
    """
    try:
        service = UserService(db)
        new_user = await service.create_user(user_data)
        logger.info(f"User {new_user.id} created by admin {current_user.id}: {new_user.email}")
        return new_user
    except ValueError as e:
        logger.warning(f"User creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
):
    """Update user details.

    Requires: MANAGE_USERS permission (Admin only)

    Args:
        user_id: User primary key
        user_data: Update data (full_name, email, password, role, is_active)

    Returns:
        HTTP 200 with updated user
        HTTP 403 if unauthorized
        HTTP 404 if user not found
        HTTP 409 if email already in use
    """
    try:
        service = UserService(db)
        updated_user = await service.update_user(user_id, user_data)

        if not updated_user:
            logger.warning(f"User {user_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        logger.info(f"User {user_id} updated by admin {current_user.id}")
        return updated_user
    except ValueError as e:
        logger.warning(f"User update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )


@router.patch("/{user_id}/role", response_model=UserResponse)
async def assign_role(
    user_id: int,
    role: UserRole,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
):
    """Assign a role to a user.

    Requires: MANAGE_USERS permission (Admin only)

    Args:
        user_id: User primary key
        role: New UserRole to assign (ADMIN, ENGINEER, OPERATOR)

    Returns:
        HTTP 200 with updated user
        HTTP 403 if unauthorized
        HTTP 404 if user not found
    """
    try:
        service = UserService(db)
        updated_user = await service.assign_role(user_id, role)

        if not updated_user:
            logger.warning(f"User {user_id} not found for role assignment")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        logger.info(f"User {user_id} role assigned to {role.value} by admin {current_user.id}")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning role to user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign role",
        )


@router.patch("/{user_id}/enable", response_model=UserResponse)
async def enable_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
):
    """Enable a user account.

    Requires: MANAGE_USERS permission (Admin only)

    Args:
        user_id: User primary key

    Returns:
        HTTP 200 with updated user
        HTTP 403 if unauthorized
        HTTP 404 if user not found
    """
    try:
        service = UserService(db)
        updated_user = await service.enable_user(user_id)

        if not updated_user:
            logger.warning(f"User {user_id} not found for enabling")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        logger.info(f"User {user_id} enabled by admin {current_user.id}")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable user",
        )


@router.patch("/{user_id}/disable", response_model=UserResponse)
async def disable_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
):
    """Disable a user account.

    Requires: MANAGE_USERS permission (Admin only)

    Args:
        user_id: User primary key

    Returns:
        HTTP 200 with updated user
        HTTP 403 if unauthorized
        HTTP 404 if user not found
    """
    try:
        service = UserService(db)
        updated_user = await service.disable_user(user_id)

        if not updated_user:
            logger.warning(f"User {user_id} not found for disabling")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        logger.info(f"User {user_id} disabled by admin {current_user.id}")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable user",
        )
