"""Dashboard service for aggregating machine telemetry and alert data."""

import asyncio
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.alert_repository import AlertRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.telemetry_repository import TelemetryRepository

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for aggregating dashboard data from multiple repositories."""

    def __init__(self, db: AsyncSession):
        """Initialize service with async database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db
        self.telemetry_repo = TelemetryRepository(db)
        self.prediction_repo = PredictionRepository(db)
        self.alert_repo = AlertRepository(db)

    async def get_dashboard_overview(self, machine_id: int) -> dict:
        """Get comprehensive dashboard overview for a machine.

        Aggregates latest telemetry, prediction, alert, and counts.
        Executes repository calls concurrently for performance.

        Args:
            machine_id: Machine identifier

        Returns:
            Dictionary with dashboard data:
                - latest_telemetry: Latest telemetry record (or None)
                - latest_prediction: Latest prediction record (or None)
                - latest_alert: Latest alert record (or None)
                - telemetry_count: Total telemetry records for machine
                - prediction_count: Total predictions for machine
                - alert_count: Total alerts for machine
                - machine_id: Echo back the requested machine_id

        Raises:
            Exception: If database operations fail
        """
        try:
            # Execute all repository calls concurrently
            (
                latest_telemetry,
                latest_prediction,
                latest_alert,
                telemetry_count,
                prediction_count,
                alert_count,
            ) = await asyncio.gather(
                self.telemetry_repo.get_latest(machine_id),
                self.prediction_repo.get_latest(machine_id),
                self.alert_repo.get_latest(machine_id),
                self.telemetry_repo.count(machine_id),
                self.prediction_repo.count(machine_id),
                self.alert_repo.count(machine_id),
                return_exceptions=True,
            )

            # Handle any exceptions from concurrent calls
            if isinstance(latest_telemetry, Exception):
                logger.error(f"Error fetching latest telemetry: {latest_telemetry}")
                latest_telemetry = None
            if isinstance(latest_prediction, Exception):
                logger.error(f"Error fetching latest prediction: {latest_prediction}")
                latest_prediction = None
            if isinstance(latest_alert, Exception):
                logger.error(f"Error fetching latest alert: {latest_alert}")
                latest_alert = None
            if isinstance(telemetry_count, Exception):
                logger.error(f"Error counting telemetry: {telemetry_count}")
                telemetry_count = 0
            if isinstance(prediction_count, Exception):
                logger.error(f"Error counting predictions: {prediction_count}")
                prediction_count = 0
            if isinstance(alert_count, Exception):
                logger.error(f"Error counting alerts: {alert_count}")
                alert_count = 0

            # Aggregate into dashboard overview
            overview = {
                "machine_id": machine_id,
                "latest_telemetry": latest_telemetry,
                "latest_prediction": latest_prediction,
                "latest_alert": latest_alert,
                "telemetry_count": telemetry_count,
                "prediction_count": prediction_count,
                "alert_count": alert_count,
            }

            logger.info(
                f"Dashboard overview retrieved for machine {machine_id}: "
                f"telemetry={telemetry_count}, predictions={prediction_count}, alerts={alert_count}"
            )

            return overview

        except Exception as e:
            logger.error(f"Error generating dashboard overview: {str(e)}")
            raise
