"""Asset model for IoT device management."""

from datetime import date

from sqlalchemy import Date, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import MachineStatus
from app.models.base import BaseModel


class Asset(BaseModel):
    """Asset model for storing IoT device/machine information."""

    __tablename__ = "assets"
    __allow_unmapped__ = True

    asset_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    asset_name: Mapped[str] = mapped_column(String(200), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(150), nullable=True)
    model_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    installation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[MachineStatus] = mapped_column(Enum(MachineStatus), nullable=False)
