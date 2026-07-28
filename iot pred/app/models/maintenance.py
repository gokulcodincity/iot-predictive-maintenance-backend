"""Maintenance record model for tracking equipment maintenance operations."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import MaintenanceStatus
from app.models.base import BaseModel


class Maintenance(BaseModel):
    """Maintenance record model for tracking equipment maintenance."""

    __tablename__ = "maintenance_records"
    __allow_unmapped__ = True

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"), nullable=False, index=True
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[MaintenanceStatus] = mapped_column(
        Enum(MaintenanceStatus), default=MaintenanceStatus.PENDING, nullable=False
    )
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
