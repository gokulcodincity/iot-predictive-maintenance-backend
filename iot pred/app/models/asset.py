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
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[MachineStatus] = mapped_column(Enum(MachineStatus), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(150), nullable=False)
    model_number: Mapped[str] = mapped_column(String(100), nullable=False)
    installation_date: Mapped[date] = mapped_column(Date, nullable=False)
