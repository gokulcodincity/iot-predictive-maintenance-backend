"""Dashboard API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{machine_id}")
async def get_dashboard(
    machine_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Get comprehensive dashboard overview for a machine.

    Aggregates latest telemetry, prediction, alert data and record counts.
    Provides real-time snapshot of machine health status.

    Args:
        machine_id: Machine identifier

    Returns:
        HTTP 200 with dashboard overview dictionary:
            - machine_id: Target machine
            - latest_telemetry: Most recent sensor reading (or None)
            - latest_prediction: Most recent ML inference (or None)
            - latest_alert: Most recent alert/notification (or None)
            - telemetry_count: Total sensor readings for machine
            - prediction_count: Total predictions for machine
            - alert_count: Total alerts for machine

    Raises:
        HTTP 500: If dashboard data aggregation fails
    """
    try:
        service = DashboardService(db)
        overview = await service.get_dashboard_overview(machine_id)

        logger.info(
            f"Dashboard overview retrieved for machine {machine_id}: "
            f"telemetry={overview.get('telemetry_count')}, "
            f"predictions={overview.get('prediction_count')}, "
            f"alerts={overview.get('alert_count')}"
        )
        return overview

    except Exception as e:
        logger.error(f"Error retrieving dashboard overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard overview",
        )
