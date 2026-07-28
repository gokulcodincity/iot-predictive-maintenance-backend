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


class MaintenanceStatus(str, Enum):
    """Maintenance record status values."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ApprovalStatus(str, Enum):
    """Approval workflow status values."""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
