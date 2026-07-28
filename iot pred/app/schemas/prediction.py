"""Prediction schemas for request and response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.prediction import PredictionStatus


class PredictionCreate(BaseModel):
    """Schema for creating a new prediction."""

    machine_id: int
    telemetry_id: int
    anomaly_score: float = Field(ge=0, le=1)
    failure_risk: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    prediction_status: PredictionStatus
    model_version: str
    inference_time_ms: int = Field(ge=0)


class PredictionResponse(BaseModel):
    """Schema for prediction response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    machine_id: int
    telemetry_id: int
    anomaly_score: float
    failure_risk: float
    confidence: float
    prediction_status: PredictionStatus
    model_version: str
    inference_time_ms: int
    created_at: datetime
