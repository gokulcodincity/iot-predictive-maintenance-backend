"""Telemetry API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.repositories.telemetry_repository import TelemetryRepository
from app.schemas.telemetry import TelemetryResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.get("/latest/{machine_id}", response_model=TelemetryResponse)
async def get_latest_telemetry(
    machine_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Get the latest telemetry reading for a machine.

    Args:
        machine_id: Machine identifier

    Returns:
        HTTP 200 with latest telemetry record
        HTTP 404 if no telemetry found for machine
    """
    try:
        repo = TelemetryRepository(db)
        telemetry = await repo.get_latest(machine_id)

        if not telemetry:
            logger.warning(f"No telemetry found for machine {machine_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No telemetry found for machine {machine_id}",
            )

        logger.info(f"Retrieved latest telemetry for machine {machine_id}")
        return telemetry

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest telemetry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve telemetry",
        )


@router.get("/history/{machine_id}", response_model=list[TelemetryResponse])
async def get_telemetry_history(
    machine_id: int,
    limit: int = Query(100, ge=1, le=10000),
    db: AsyncSession = Depends(get_async_session),
):
    """Get telemetry history for a machine (newest first).

    Args:
        machine_id: Machine identifier
        limit: Maximum number of records (default 100, max 10000)

    Returns:
        HTTP 200 with list of telemetry records
    """
    try:
        repo = TelemetryRepository(db)
        telemetry_records = await repo.get_by_machine(machine_id, limit=limit)

        logger.info(f"Retrieved {len(telemetry_records)} telemetry records for machine {machine_id}")
        return telemetry_records

    except Exception as e:
        logger.error(f"Error retrieving telemetry history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve telemetry history",
        )


@router.get("/range/{machine_id}", response_model=list[TelemetryResponse])
async def get_telemetry_range(
    machine_id: int,
    start_time: str = Query(..., description="Start timestamp (ISO format)"),
    end_time: str = Query(..., description="End timestamp (ISO format)"),
    db: AsyncSession = Depends(get_async_session),
):
    """Get telemetry within a time range for a machine.

    Args:
        machine_id: Machine identifier
        start_time: Start timestamp (ISO format, e.g., 2026-07-28T00:00:00)
        end_time: End timestamp (ISO format, e.g., 2026-07-28T23:59:59)

    Returns:
        HTTP 200 with list of telemetry records within time range
    """
    try:
        repo = TelemetryRepository(db)
        telemetry_records = await repo.get_by_timerange(machine_id, start_time, end_time)

        logger.info(
            f"Retrieved {len(telemetry_records)} telemetry records for machine {machine_id} "
            f"from {start_time} to {end_time}"
        )
        return telemetry_records

    except ValueError as e:
        logger.error(f"Invalid timestamp format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid timestamp format: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error retrieving telemetry range: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve telemetry range",
        )


@router.get("/count/{machine_id}", response_model=dict)
async def get_telemetry_count(
    machine_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Get total telemetry count for a machine.

    Args:
        machine_id: Machine identifier

    Returns:
        HTTP 200 with count dictionary
    """
    try:
        repo = TelemetryRepository(db)
        count = await repo.count(machine_id)

        logger.info(f"Machine {machine_id} has {count} telemetry records")
        return {"machine_id": machine_id, "count": count}

    except Exception as e:
        logger.error(f"Error counting telemetry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count telemetry records",
        )


@router.get("/exists", response_model=dict)
async def check_telemetry_exists(
    machine_id: int = Query(..., description="Machine identifier"),
    timestamp: str = Query(..., description="Timestamp to check (ISO format)"),
    db: AsyncSession = Depends(get_async_session),
):
    """Check if telemetry exists for a machine at a specific timestamp.

    Args:
        machine_id: Machine identifier
        timestamp: Timestamp to check (ISO format)

    Returns:
        HTTP 200 with exists boolean
    """
    try:
        repo = TelemetryRepository(db)
        exists = await repo.exists(machine_id, timestamp)

        logger.info(
            f"Telemetry exists for machine {machine_id} at {timestamp}: {exists}"
        )
        return {"machine_id": machine_id, "timestamp": timestamp, "exists": exists}

    except ValueError as e:
        logger.error(f"Invalid timestamp format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid timestamp format: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error checking telemetry existence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check telemetry existence",
        )
