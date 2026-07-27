"""Asset schemas for request and response validation."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.core.constants import MachineStatus


class AssetCreate(BaseModel):
    """Schema for creating a new asset."""

    asset_code: str
    asset_name: str
    asset_type: str
    location: str
    status: MachineStatus
    manufacturer: str | None = None
    model_number: str | None = None
    installation_date: date | None = None


class AssetUpdate(BaseModel):
    """Schema for updating an asset."""

    asset_code: str | None = None
    asset_name: str | None = None
    asset_type: str | None = None
    location: str | None = None
    status: MachineStatus | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    installation_date: date | None = None


class AssetResponse(BaseModel):
    """Schema for asset response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_code: str
    asset_name: str
    asset_type: str
    location: str
    status: MachineStatus
    manufacturer: str | None
    model_number: str | None
    installation_date: date | None
    created_at: datetime
    updated_at: datetime
