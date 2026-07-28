"""Alert API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert_schemas import AlertResponse, AlertUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alert", tags=["Alert"])


@router.get("/latest/{machine_id}", response_model=AlertResponse)
async def get_latest_alert(
    machine_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Get the latest alert for a machine.

    Args:
        machine_id: Machine identifier

    Returns:
        HTTP 200 with latest alert record
        HTTP 404 if no alert found for machine
    """
    try:
        repo = AlertRepository(db)
        alert = await repo.get_latest(machine_id)

        if not alert:
            logger.warning(f"No alert found for machine {machine_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No alert found for machine {machine_id}",
            )

        logger.info(f"Retrieved latest alert for machine {machine_id}")
        return alert

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert",
        )


@router.get("/history/{machine_id}", response_model=list[AlertResponse])
async def get_alert_history(
    machine_id: int,
    limit: int = Query(100, ge=1, le=10000),
    db: AsyncSession = Depends(get_async_session),
):
    """Get alert history for a machine (newest first).

    Args:
        machine_id: Machine identifier
        limit: Maximum number of records (default 100, max 10000)

    Returns:
        HTTP 200 with list of alert records
    """
    try:
        repo = AlertRepository(db)
        alerts = await repo.get_by_machine(machine_id, limit=limit)

        logger.info(f"Retrieved {len(alerts)} alerts for machine {machine_id}")
        return alerts

    except Exception as e:
        logger.error(f"Error retrieving alert history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert history",
        )


@router.get("/count/{machine_id}", response_model=dict)
async def get_alert_count(
    machine_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Get total alert count for a machine.

    Args:
        machine_id: Machine identifier

    Returns:
        HTTP 200 with count dictionary
    """
    try:
        repo = AlertRepository(db)
        count = await repo.count(machine_id)

        logger.info(f"Machine {machine_id} has {count} alerts")
        return {"machine_id": machine_id, "count": count}

    except Exception as e:
        logger.error(f"Error counting alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count alerts",
        )


@router.get("/range/{machine_id}", response_model=list[AlertResponse])
async def get_alert_range(
    machine_id: int,
    start_time: str = Query(..., description="Start timestamp (ISO format)"),
    end_time: str = Query(..., description="End timestamp (ISO format)"),
    db: AsyncSession = Depends(get_async_session),
):
    """Get alerts within a time range for a machine.

    Args:
        machine_id: Machine identifier
        start_time: Start timestamp (ISO format, e.g., 2026-07-28T00:00:00)
        end_time: End timestamp (ISO format, e.g., 2026-07-28T23:59:59)

    Returns:
        HTTP 200 with list of alerts within time range
    """
    try:
        repo = AlertRepository(db)
        alerts = await repo.get_by_timerange(machine_id, start_time, end_time)

        logger.info(
            f"Retrieved {len(alerts)} alerts for machine {machine_id} "
            f"from {start_time} to {end_time}"
        )
        return alerts

    except ValueError as e:
        logger.error(f"Invalid timestamp format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid timestamp format: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error retrieving alert range: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert range",
        )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Get a specific alert by ID.

    Args:
        alert_id: Alert identifier

    Returns:
        HTTP 200 with alert record
        HTTP 404 if alert not found
    """
    try:
        repo = AlertRepository(db)
        alert = await repo.get_by_id(alert_id)

        if not alert:
            logger.warning(f"Alert {alert_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert {alert_id} not found",
            )

        logger.info(f"Retrieved alert {alert_id}")
        return alert

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert",
        )


@router.put("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Acknowledge an alert (mark as read by operator).

    Args:
        alert_id: Alert identifier

    Returns:
        HTTP 200 with updated alert record
        HTTP 404 if alert not found
    """
    try:
        repo = AlertRepository(db)
        alert = await repo.acknowledge(alert_id)

        if not alert:
            logger.warning(f"Alert {alert_id} not found for acknowledgement")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert {alert_id} not found",
            )

        logger.info(f"Alert {alert_id} acknowledged by operator")
        return alert

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert",
        )
