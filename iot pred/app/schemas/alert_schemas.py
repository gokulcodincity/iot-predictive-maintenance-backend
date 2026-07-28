"""Alert schemas for request and response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.alert import AlertSeverity, AlertStatus


class AlertCreate(BaseModel):
    """Schema for creating a new alert."""

    machine_id: int = Field(gt=0)
    prediction_id: int | None = None
    severity: AlertSeverity
    priority: str = Field(min_length=1, max_length=10)
    message: str = Field(min_length=10, max_length=1000)
    final_action: str = Field(min_length=1, max_length=100)
    prediction_status: str = Field(min_length=1, max_length=50)
    failure_risk: float = Field(ge=0.0, le=1.0)
    anomaly_score: float = Field(ge=0.0, le=1.0)
    requires_acknowledgement: bool = True
    status: AlertStatus = AlertStatus.PENDING


class AlertUpdate(BaseModel):
    """Schema for updating an alert (acknowledgement only)."""

    status: AlertStatus


class AlertResponse(BaseModel):
    """Schema for alert response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int
    prediction_id: int | None
    severity: AlertSeverity
    priority: str
    message: str
    final_action: str
    prediction_status: str
    failure_risk: float
    anomaly_score: float
    requires_acknowledgement: bool
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
