"""Telemetry API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.telemetry import TelemetryCreate, TelemetryResponse
from app.services.telemetry_service import TelemetryService

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.post("", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
async def create_telemetry(
    telemetry_data: TelemetryCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new telemetry reading from sensor data.

    Request body contains sensor readings from AWS IoT Core/Lambda.

    Returns:
        HTTP 201 with created telemetry record
    """
    service = TelemetryService(db)
    return await service.create_telemetry(telemetry_data)


@router.get("/machine/{machine_id}/latest", response_model=TelemetryResponse)
async def get_latest_machine_telemetry(
    machine_id: int, db: AsyncSession = Depends(get_db)
):
    """Get the latest telemetry reading for a specific machine.

    Args:
        machine_id: Asset/machine primary key

    Returns:
        HTTP 200 with latest telemetry record (by timestamp)
        HTTP 404 if no telemetry found for machine
    """
    service = TelemetryService(db)
    return await service.get_latest_telemetry(machine_id)


@router.get("/machine/{machine_id}", response_model=list[TelemetryResponse])
async def get_machine_telemetry(
    machine_id: int, db: AsyncSession = Depends(get_db)
):
    """Get all telemetry readings for a specific machine.

    Args:
        machine_id: Asset/machine primary key

    Returns:
        HTTP 200 with list of telemetry readings (newest first)
    """
    service = TelemetryService(db)
    return await service.get_machine_telemetry(machine_id)


@router.get("/{telemetry_id}", response_model=TelemetryResponse)
async def get_telemetry(telemetry_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific telemetry record by id.

    Args:
        telemetry_id: Telemetry primary key

    Returns:
        HTTP 200 with telemetry record
        HTTP 404 if not found
    """
    service = TelemetryService(db)
    return await service.get_telemetry_by_id(telemetry_id)


@router.get("", response_model=list[TelemetryResponse])
async def list_telemetry(db: AsyncSession = Depends(get_db)):
    """Get all telemetry records.

    Returns:
        HTTP 200 with list of all telemetry readings
    """
    service = TelemetryService(db)
    return await service.get_all_telemetry()
