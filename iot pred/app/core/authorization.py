"""Role-Based Access Control (RBAC) authorization system."""

from enum import Enum
from typing import Set


class Role(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"
    PLANT_MANAGER = "plant_manager"
    MAINTENANCE_ENGINEER = "maintenance_engineer"
    RELIABILITY_ENGINEER = "reliability_engineer"


class Permission(str, Enum):
    """Permissions for different operations."""

    # User Management
    MANAGE_USERS = "manage_users"

    # Asset Management
    MANAGE_ASSETS = "manage_assets"
    VIEW_ASSETS = "view_assets"

    # System Configuration
    CONFIGURE_SYSTEM = "configure_system"

    # Dashboard and Reports
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_REPORTS = "view_reports"

    # Telemetry
    VIEW_TELEMETRY = "view_telemetry"

    # Predictions and Alerts
    VIEW_PREDICTIONS = "view_predictions"
    VIEW_ALERTS = "view_alerts"
    VIEW_RECOMMENDATIONS = "view_recommendations"

    # Maintenance
    CREATE_MAINTENANCE = "create_maintenance"
    UPDATE_MAINTENANCE = "update_maintenance"

    # Trends and Validation
    VIEW_TRENDS = "view_trends"
    VALIDATE_AI_RESULTS = "validate_ai_results"


# Role-to-Permission mapping (minimal, role-based)
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # User Management
        Permission.MANAGE_USERS,
        # Asset Management
        Permission.MANAGE_ASSETS,
        Permission.VIEW_ASSETS,
        # System Configuration
        Permission.CONFIGURE_SYSTEM,
        # Dashboard and Reports
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_REPORTS,
        # Telemetry
        Permission.VIEW_TELEMETRY,
        # Predictions and Alerts
        Permission.VIEW_PREDICTIONS,
        Permission.VIEW_ALERTS,
        Permission.VIEW_RECOMMENDATIONS,
        # Maintenance
        Permission.CREATE_MAINTENANCE,
        Permission.UPDATE_MAINTENANCE,
        # Trends and Validation
        Permission.VIEW_TRENDS,
        Permission.VALIDATE_AI_RESULTS,
    },
    Role.PLANT_MANAGER: {
        # Dashboard and Reports
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_REPORTS,
        # Assets
        Permission.VIEW_ASSETS,
    },
    Role.MAINTENANCE_ENGINEER: {
        # Telemetry
        Permission.VIEW_TELEMETRY,
        # Alerts and Recommendations
        Permission.VIEW_ALERTS,
        Permission.VIEW_RECOMMENDATIONS,
        # Maintenance
        Permission.CREATE_MAINTENANCE,
        Permission.UPDATE_MAINTENANCE,
    },
    Role.RELIABILITY_ENGINEER: {
        # Telemetry
        Permission.VIEW_TELEMETRY,
        # Predictions
        Permission.VIEW_PREDICTIONS,
        # Trends and Validation
        Permission.VIEW_TRENDS,
        Permission.VALIDATE_AI_RESULTS,
    },
}


def get_role_permissions(role: Role) -> Set[Permission]:
    """Get all permissions for a given role.

    Args:
        role: Role enum value

    Returns:
        Set of Permission enums for the role

    Raises:
        ValueError: If role is invalid
    """
    if not isinstance(role, Role):
        raise ValueError(f"Invalid role: {role}")

    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: Role, permission: Permission) -> bool:
    """Check if a role has a specific permission.

    Args:
        role: Role enum value
        permission: Permission enum value

    Returns:
        True if role has permission, False otherwise

    Example:
        >>> has_permission(Role.ADMIN, Permission.MANAGE_USERS)
        True
        >>> has_permission(Role.MAINTENANCE_ENGINEER, Permission.MANAGE_USERS)
        False
    """
    permissions = get_role_permissions(role)
    return permission in permissions


def has_any_permission(role: Role, permissions: Set[Permission]) -> bool:
    """Check if a role has any of the given permissions.

    Args:
        role: Role enum value
        permissions: Set of Permission enums to check

    Returns:
        True if role has at least one of the permissions, False otherwise

    Example:
        >>> has_any_permission(Role.ADMIN, {Permission.MANAGE_USERS, Permission.MANAGE_ASSETS})
        True
    """
    role_permissions = get_role_permissions(role)
    return bool(role_permissions & permissions)


def has_all_permissions(role: Role, permissions: Set[Permission]) -> bool:
    """Check if a role has all of the given permissions.

    Args:
        role: Role enum value
        permissions: Set of Permission enums to check

    Returns:
        True if role has all permissions, False otherwise

    Example:
        >>> has_all_permissions(Role.ADMIN, {Permission.MANAGE_USERS, Permission.MANAGE_ASSETS})
        True
    """
    role_permissions = get_role_permissions(role)
    return permissions.issubset(role_permissions)
