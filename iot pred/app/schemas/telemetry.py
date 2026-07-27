"""Telemetry schemas for request and response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelemetryCreate(BaseModel):
    """Schema for creating a new telemetry reading."""

    machine_id: int
    temperature: float = Field(ge=0)
    vibration: float = Field(ge=0)
    current: float = Field(ge=0)
    speed: float = Field(ge=0)
    throughput: float = Field(ge=0)
    timestamp: datetime


class TelemetryResponse(BaseModel):
    """Schema for telemetry response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int
    temperature: float = Field(ge=0)
    vibration: float = Field(ge=0)
    current: float = Field(ge=0)
    speed: float = Field(ge=0)
    throughput: float = Field(ge=0)
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
