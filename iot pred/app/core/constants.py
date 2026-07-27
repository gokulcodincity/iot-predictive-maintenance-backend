"""Application constants and enums."""

from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    ENGINEER = "engineer"
    OPERATOR = "operator"


class MachineStatus(str, Enum):
    """Status of industrial machines/assets."""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PredictionStatus(str, Enum):
    """Prediction status values."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
