"""Alert repository for database operations."""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, AlertStatus
from app.schemas.alert_schemas import AlertCreate

logger = logging.getLogger(__name__)


class AlertRepository:
    """Repository for alert database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with async database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db

    async def create(self, alert_data: AlertCreate) -> Alert:
        """Create a new alert record.

        Args:
            alert_data: AlertCreate schema with alert values

        Returns:
            Created Alert object with id and timestamps populated

        Raises:
            Exception: If database operation fails
        """
        try:
            alert = Alert(
                machine_id=alert_data.machine_id,
                prediction_id=alert_data.prediction_id,
                severity=alert_data.severity,
                priority=alert_data.priority,
                message=alert_data.message,
                final_action=alert_data.final_action,
                prediction_status=alert_data.prediction_status,
                failure_risk=alert_data.failure_risk,
                anomaly_score=alert_data.anomaly_score,
                requires_acknowledgement=alert_data.requires_acknowledgement,
                status=alert_data.status,
            )

            self.db.add(alert)
            await self.db.flush()
            await self.db.refresh(alert)

            logger.info(f"Alert created for machine {alert_data.machine_id} (severity={alert_data.severity.value})")
            return alert

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error creating alert: {str(e)}")
            raise

    async def get_by_id(self, alert_id: int) -> Optional[Alert]:
        """Get alert record by primary key.

        Args:
            alert_id: Alert primary key

        Returns:
            Alert object or None if not found
        """
        try:
            result = await self.db.execute(
                select(Alert).where(Alert.id == alert_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Database error retrieving alert by id: {str(e)}")
            raise

    async def get_all(self) -> List[Alert]:
        """Get all alert records.

        Returns:
            List of all Alert objects
        """
        try:
            result = await self.db.execute(select(Alert))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Database error retrieving all alerts: {str(e)}")
            raise

    async def get_latest(self, machine_id: int) -> Optional[Alert]:
        """Get most recent alert for a machine.

        Args:
            machine_id: Machine identifier

        Returns:
            Latest Alert object for the machine or None
        """
        try:
            result = await self.db.execute(
                select(Alert)
                .where(Alert.machine_id == machine_id)
                .order_by(Alert.created_at.desc())
                .limit(1)
            )

            alert = result.scalar_one_or_none()

            if alert:
                logger.debug(f"Retrieved latest alert for machine {machine_id}")
            else:
                logger.debug(f"No alert found for machine {machine_id}")

            return alert

        except Exception as e:
            logger.error(f"Database error retrieving latest alert: {str(e)}")
            raise

    async def get_by_machine(
        self, machine_id: int, limit: int = 100
    ) -> List[Alert]:
        """Get alerts for a machine (newest first).

        Args:
            machine_id: Machine identifier
            limit: Maximum number of records to return (default 100)

        Returns:
            List of Alert objects ordered by created_at descending
        """
        try:
            result = await self.db.execute(
                select(Alert)
                .where(Alert.machine_id == machine_id)
                .order_by(Alert.created_at.desc())
                .limit(limit)
            )

            alerts = result.scalars().all()

            logger.debug(
                f"Retrieved {len(alerts)} alerts for machine {machine_id}"
            )

            return alerts

        except Exception as e:
            logger.error(f"Database error retrieving machine alerts: {str(e)}")
            raise

    async def get_by_timerange(
        self, machine_id: int, start_time: str, end_time: str
    ) -> List[Alert]:
        """Get alerts within time range for a machine.

        Args:
            machine_id: Machine identifier
            start_time: Start timestamp (ISO format string)
            end_time: End timestamp (ISO format string)

        Returns:
            List of Alert objects within time range, ordered by created_at ascending
        """
        try:
            # Parse timestamps
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)

            result = await self.db.execute(
                select(Alert)
                .where(
                    and_(
                        Alert.machine_id == machine_id,
                        Alert.created_at >= start_dt,
                        Alert.created_at <= end_dt,
                    )
                )
                .order_by(Alert.created_at.asc())
            )

            alerts = result.scalars().all()

            logger.debug(
                f"Retrieved {len(alerts)} alerts for machine {machine_id} "
                f"from {start_time} to {end_time}"
            )

            return alerts

        except ValueError as e:
            logger.error(f"Invalid timestamp format: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Database error retrieving alerts by timerange: {str(e)}")
            raise

    async def count(self, machine_id: int) -> int:
        """Count alerts for a machine.

        Args:
            machine_id: Machine identifier

        Returns:
            Number of alerts for the machine
        """
        try:
            result = await self.db.execute(
                select(func.count()).select_from(Alert)
                .where(Alert.machine_id == machine_id)
            )

            count = result.scalar_one()

            logger.debug(f"Machine {machine_id} has {count} alerts")

            return count

        except Exception as e:
            logger.error(f"Database error counting alerts: {str(e)}")
            raise

    async def exists(self, machine_id: int, timestamp: str) -> bool:
        """Check if alert exists for machine at timestamp.

        Args:
            machine_id: Machine identifier
            timestamp: Timestamp in ISO format string

        Returns:
            True if record exists, False otherwise
        """
        try:
            # Parse timestamp
            ts = datetime.fromisoformat(timestamp)

            result = await self.db.execute(
                select(func.count()).select_from(Alert)
                .where(
                    and_(
                        Alert.machine_id == machine_id,
                        Alert.created_at == ts,
                    )
                )
            )

            count = result.scalar_one()
            exists = count > 0

            logger.debug(
                f"Alert exists for machine {machine_id} at {timestamp}: {exists}"
            )

            return exists

        except ValueError as e:
            logger.error(f"Invalid timestamp format: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Database error checking alert existence: {str(e)}")
            raise

    async def acknowledge(self, alert_id: int) -> Optional[Alert]:
        """Mark alert as acknowledged by operator.

        Args:
            alert_id: Alert primary key

        Returns:
            Updated Alert object or None if not found

        Raises:
            Exception: If database operation fails
        """
        try:
            alert = await self.get_by_id(alert_id)

            if not alert:
                logger.warning(f"Alert {alert_id} not found for acknowledgement")
                return None

            alert.status = AlertStatus.ACKNOWLEDGED
            await self.db.flush()
            await self.db.refresh(alert)

            logger.info(f"Alert {alert_id} acknowledged")
            return alert

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error acknowledging alert: {str(e)}")
            raise
