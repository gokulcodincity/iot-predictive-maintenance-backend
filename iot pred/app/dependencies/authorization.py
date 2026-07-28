"""Authorization dependencies for role-based access control."""

import logging
from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.authorization import Permission, Role, has_permission
from app.core.constants import UserRole
from app.db.session import get_db
from app.models.user import User

logger = logging.getLogger(__name__)


# Mapping from UserRole (database) to Role (RBAC system)
USERROLE_TO_RBAC_ROLE: dict[UserRole, Role] = {
    UserRole.ADMIN: Role.ADMIN,
    UserRole.ENGINEER: Role.RELIABILITY_ENGINEER,  # Engineers do analysis/validation
    UserRole.OPERATOR: Role.MAINTENANCE_ENGINEER,  # Operators handle maintenance
}


def get_user_rbac_role(user: User) -> Role:
    """Convert user's database role to RBAC role enum.

    Args:
        user: User model with role field

    Returns:
        Role enum for authorization checks

    Raises:
        ValueError: If user role cannot be mapped
    """
    if not hasattr(user, "role"):
        logger.error(f"User {user.id} has no role attribute")
        raise ValueError("User role not found")

    rbac_role = USERROLE_TO_RBAC_ROLE.get(user.role)
    if not rbac_role:
        logger.error(f"Unknown role {user.role} for user {user.id}")
        raise ValueError(f"Unknown user role: {user.role}")

    return rbac_role


def require_permission(permission: Permission) -> Callable:
    """Create a dependency that requires a specific permission.

    Args:
        permission: Permission enum to check

    Returns:
        FastAPI dependency function

    Example:
        >>> @router.post("/users")
        >>> async def create_user(
        >>>     current_user = Depends(require_permission(Permission.MANAGE_USERS))
        >>> ):
        >>>     return {"user": current_user.email}

    Raises:
        HTTPException: 403 if user lacks permission
    """

    async def check_permission(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Verify user has required permission.

        Args:
            current_user: Authenticated user from JWT token

        Returns:
            Authenticated user if authorized

        Raises:
            HTTPException(403): If user lacks permission
        """
        try:
            # Convert user's database role to RBAC role
            user_role = get_user_rbac_role(current_user)

            # Check if user has the required permission
            if not has_permission(user_role, permission):
                logger.warning(
                    f"Permission denied: user {current_user.id} "
                    f"({user_role.value}) lacks {permission.value}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied",
                )

            logger.debug(
                f"Permission granted: user {current_user.id} "
                f"({user_role.value}) has {permission.value}"
            )
            return current_user

        except ValueError as e:
            logger.error(f"Role mapping error for user {current_user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

    return check_permission


def require_any_permission(*permissions: Permission) -> Callable:
    """Create a dependency that requires at least one of several permissions.

    Args:
        *permissions: Variable number of Permission enums

    Returns:
        FastAPI dependency function

    Example:
        >>> @router.get("/dashboard")
        >>> async def get_dashboard(
        >>>     current_user = Depends(require_any_permission(
        >>>         Permission.VIEW_DASHBOARD,
        >>>         Permission.VIEW_REPORTS
        >>>     ))
        >>> ):
        >>>     return {"dashboard": "data"}

    Raises:
        HTTPException: 403 if user lacks all permissions
    """
    permission_set = set(permissions)

    async def check_any_permission(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Verify user has at least one required permission.

        Args:
            current_user: Authenticated user from JWT token

        Returns:
            Authenticated user if authorized

        Raises:
            HTTPException(403): If user lacks all permissions
        """
        try:
            # Convert user's database role to RBAC role
            user_role = get_user_rbac_role(current_user)

            # Check if user has at least one permission
            from app.core.authorization import has_any_permission

            if not has_any_permission(user_role, permission_set):
                logger.warning(
                    f"Permission denied: user {current_user.id} "
                    f"({user_role.value}) lacks all required permissions"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied",
                )

            logger.debug(
                f"Permission granted: user {current_user.id} "
                f"({user_role.value}) has required permission"
            )
            return current_user

        except ValueError as e:
            logger.error(f"Role mapping error for user {current_user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

    return check_any_permission


def require_role(*roles: Role) -> Callable:
    """Create a dependency that requires one of several roles.

    Args:
        *roles: Variable number of Role enums

    Returns:
        FastAPI dependency function

    Example:
        >>> @router.post("/system-config")
        >>> async def configure_system(
        >>>     current_user = Depends(require_role(Role.ADMIN))
        >>> ):
        >>>     return {"status": "configured"}

    Raises:
        HTTPException: 403 if user has wrong role
    """
    role_set = set(roles)

    async def check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Verify user has one of the required roles.

        Args:
            current_user: Authenticated user from JWT token

        Returns:
            Authenticated user if authorized

        Raises:
            HTTPException(403): If user has wrong role
        """
        try:
            # Convert user's database role to RBAC role
            user_role = get_user_rbac_role(current_user)

            # Check if user has one of the required roles
            if user_role not in role_set:
                logger.warning(
                    f"Role check failed: user {current_user.id} "
                    f"({user_role.value}) not in required roles"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied",
                )

            logger.debug(
                f"Role check passed: user {current_user.id} "
                f"({user_role.value}) has required role"
            )
            return current_user

        except ValueError as e:
            logger.error(f"Role mapping error for user {current_user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

    return check_role
