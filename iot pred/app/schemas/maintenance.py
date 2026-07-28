"""Maintenance schemas for request and response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import MaintenanceStatus


class MaintenanceCreate(BaseModel):
    """Schema for creating a new maintenance record."""

    asset_id: int = Field(gt=0, description="Asset/machine ID")
    maintenance_type: str = Field(
        min_length=1, max_length=100, description="Type of maintenance"
    )
    description: str = Field(
        min_length=1, max_length=500, description="Maintenance description"
    )
    status: MaintenanceStatus = Field(
        default=MaintenanceStatus.PENDING, description="Initial status"
    )
    scheduled_date: datetime | None = Field(
        default=None, description="Scheduled maintenance date"
    )


class MaintenanceUpdate(BaseModel):
    """Schema for updating a maintenance record."""

    maintenance_type: str | None = Field(
        default=None, max_length=100, description="Type of maintenance"
    )
    description: str | None = Field(
        default=None, max_length=500, description="Maintenance description"
    )
    status: MaintenanceStatus | None = Field(
        default=None, description="Maintenance status"
    )
    scheduled_date: datetime | None = Field(
        default=None, description="Scheduled maintenance date"
    )
    completed_date: datetime | None = Field(
        default=None, description="Maintenance completion date"
    )


class MaintenanceResponse(BaseModel):
    """Schema for maintenance record response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    created_by: int
    maintenance_type: str
    description: str
    status: MaintenanceStatus
    scheduled_date: datetime | None
    completed_date: datetime | None
    created_at: datetime
    updated_at: datetime
