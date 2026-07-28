"""Prediction model for AI inference results."""

from enum import Enum as PyEnum

from sqlalchemy import Enum, ForeignKey, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PredictionStatus(PyEnum):
    """Status classification of the prediction."""

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class Prediction(BaseModel):
    """Prediction model for storing AI inference results from ML models."""

    __tablename__ = "predictions"
    __allow_unmapped__ = True

    machine_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"), nullable=False, index=True
    )
    telemetry_id: Mapped[int] = mapped_column(
        ForeignKey("telemetry.id"), nullable=False, index=True
    )
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    failure_risk: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    prediction_status: Mapped[PredictionStatus] = mapped_column(
        Enum(PredictionStatus), nullable=False, index=True
    )
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    inference_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    asset: Mapped["Asset"] = relationship("Asset", foreign_keys=[machine_id])
    telemetry: Mapped["Telemetry"] = relationship(
        "Telemetry", foreign_keys=[telemetry_id]
    )
