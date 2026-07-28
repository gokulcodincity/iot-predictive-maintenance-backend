"""Alert model for storing machine failure alerts."""

from enum import Enum as PyEnum

from sqlalchemy import Boolean, Enum, ForeignKey, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class AlertSeverity(PyEnum):
    """Severity level of the alert."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertStatus(PyEnum):
    """Acknowledgement status of the alert."""

    ACKNOWLEDGED = "acknowledged"
    PENDING = "pending"


class Alert(BaseModel):
    """Alert model for storing machine failure alerts and maintenance notifications."""

    __tablename__ = "alerts"
    __allow_unmapped__ = True

    machine_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"), nullable=False, index=True
    )
    prediction_id: Mapped[int | None] = mapped_column(
        ForeignKey("predictions.id"), nullable=True, index=True
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity), nullable=False, index=True
    )
    priority: Mapped[str] = mapped_column(String(10), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    final_action: Mapped[str] = mapped_column(String(100), nullable=False)
    prediction_status: Mapped[str] = mapped_column(String(50), nullable=False)
    failure_risk: Mapped[float] = mapped_column(Float, nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    requires_acknowledgement: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus), nullable=False, default=AlertStatus.PENDING, index=True
    )

    asset: Mapped["Asset"] = relationship("Asset", foreign_keys=[machine_id])
    prediction: Mapped["Prediction"] = relationship(
        "Prediction", foreign_keys=[prediction_id]
    )
