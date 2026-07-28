"""Recommendation service for generating operator recommendations."""

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import AlertSeverity
from app.repositories.alert_repository import AlertRepository
from app.repositories.prediction_repository import PredictionRepository

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating operator recommendations from machine data."""

    # Recommendation templates by severity
    RECOMMENDATION_TEMPLATES = {
        AlertSeverity.CRITICAL: (
            "Immediate shutdown is recommended to avoid equipment failure.",
            "IMMEDIATE_SHUTDOWN",
        ),
        AlertSeverity.HIGH: (
            "Schedule urgent maintenance immediately.",
            "URGENT_MAINTENANCE",
        ),
        AlertSeverity.MEDIUM: (
            "Plan maintenance during the next maintenance window.",
            "SCHEDULE_MAINTENANCE",
        ),
        AlertSeverity.LOW: (
            "Continue monitoring machine health.",
            "CONTINUE_MONITORING",
        ),
    }

    def __init__(self, db: AsyncSession):
        """Initialize service with async database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db
        self.prediction_repo = PredictionRepository(db)
        self.alert_repo = AlertRepository(db)

    async def get_recommendation(self, machine_id: int) -> dict:
        """Generate operator recommendation for a machine.

        Retrieves latest prediction and alert data, applies business rules
        to generate a structured recommendation.

        Args:
            machine_id: Machine identifier

        Returns:
            Dictionary with recommendation data:
                - machine_id: Machine identifier
                - recommendation: Text recommendation for operator
                - recommended_action: Action code (IMMEDIATE_SHUTDOWN, etc.)
                - severity: Alert severity or "UNKNOWN"
                - failure_risk: Failure probability (0-1) or None
                - anomaly_score: Anomaly magnitude (0-1) or None
                - generated_at: ISO format UTC timestamp

        Raises:
            Exception: If database operations fail
        """
        try:
            # Fetch latest prediction and alert concurrently
            latest_prediction = await self.prediction_repo.get_latest(machine_id)
            latest_alert = await self.alert_repo.get_latest(machine_id)

            # Determine recommendation based on available data
            if not latest_prediction or not latest_alert:
                logger.debug(
                    f"No prediction or alert available for machine {machine_id}, "
                    "returning default recommendation"
                )
                return {
                    "machine_id": machine_id,
                    "recommendation": "No recommendation available.",
                    "recommended_action": "CONTINUE_MONITORING",
                    "severity": "UNKNOWN",
                    "failure_risk": None,
                    "anomaly_score": None,
                    "generated_at": datetime.utcnow().isoformat(),
                }

            # Extract severity and data from alert
            severity = latest_alert.severity
            recommendation_text, action_code = self._get_recommendation_by_severity(
                severity
            )

            # Build recommendation response
            recommendation = {
                "machine_id": machine_id,
                "recommendation": recommendation_text,
                "recommended_action": action_code,
                "severity": severity.value,
                "failure_risk": latest_prediction.failure_risk,
                "anomaly_score": latest_prediction.anomaly_score,
                "generated_at": datetime.utcnow().isoformat(),
            }

            logger.info(
                f"Recommendation generated for machine {machine_id}: "
                f"action={action_code}, severity={severity.value}"
            )

            return recommendation

        except Exception as e:
            logger.error(f"Error generating recommendation: {str(e)}")
            raise

    def _get_recommendation_by_severity(
        self, severity: AlertSeverity
    ) -> tuple[str, str]:
        """Get recommendation text and action code by severity.

        Args:
            severity: AlertSeverity enum value

        Returns:
            Tuple of (recommendation_text, action_code)
        """
        if severity in self.RECOMMENDATION_TEMPLATES:
            return self.RECOMMENDATION_TEMPLATES[severity]

        # Fallback for unknown severity
        logger.warning(f"Unknown severity: {severity}, using LOW default")
        return self.RECOMMENDATION_TEMPLATES[AlertSeverity.LOW]
