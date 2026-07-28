"""Prediction repository for database operations."""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction

logger = logging.getLogger(__name__)


class PredictionRepository:
    """Repository for prediction database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with async database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db

    async def create(self, prediction: Prediction) -> Prediction:
        """Create a new prediction record.

        Args:
            prediction: Prediction ORM object with values set

        Returns:
            Created Prediction object with id and created_at populated
        """
        try:
            self.db.add(prediction)
            await self.db.flush()
            await self.db.refresh(prediction)
            logger.info(f"Prediction created for machine {prediction.machine_id}")
            return prediction
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error creating prediction: {str(e)}")
            raise

    async def get_by_id(self, prediction_id: int) -> Optional[Prediction]:
        """Get prediction record by primary key.

        Args:
            prediction_id: Prediction primary key

        Returns:
            Prediction object or None if not found
        """
        try:
            result = await self.db.execute(
                select(Prediction).where(Prediction.id == prediction_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Database error retrieving prediction by id: {str(e)}")
            raise

    async def get_all(self) -> List[Prediction]:
        """Get all prediction records.

        Returns:
            List of all Prediction objects
        """
        try:
            result = await self.db.execute(select(Prediction))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Database error retrieving all predictions: {str(e)}")
            raise

    async def get_latest(self, machine_id: int) -> Optional[Prediction]:
        """Get most recent prediction for a machine.

        Args:
            machine_id: Machine identifier

        Returns:
            Latest Prediction object for the machine or None
        """
        try:
            result = await self.db.execute(
                select(Prediction)
                .where(Prediction.machine_id == machine_id)
                .order_by(Prediction.created_at.desc())
                .limit(1)
            )

            prediction = result.scalar_one_or_none()

            if prediction:
                logger.debug(f"Retrieved latest prediction for machine {machine_id}")
            else:
                logger.debug(f"No prediction found for machine {machine_id}")

            return prediction

        except Exception as e:
            logger.error(f"Database error retrieving latest prediction: {str(e)}")
            raise

    async def get_latest_by_machine(self, machine_id: int) -> Optional[Prediction]:
        """Get most recent prediction for a machine (legacy method).

        Args:
            machine_id: Asset/machine primary key

        Returns:
            Latest Prediction object for the machine or None
        """
        return await self.get_latest(machine_id)

    async def get_by_machine(
        self, machine_id: int, limit: int = 100
    ) -> List[Prediction]:
        """Get predictions for a machine (newest first).

        Args:
            machine_id: Machine identifier
            limit: Maximum number of records to return (default 100)

        Returns:
            List of Prediction objects ordered by created_at descending
        """
        try:
            result = await self.db.execute(
                select(Prediction)
                .where(Prediction.machine_id == machine_id)
                .order_by(Prediction.created_at.desc())
                .limit(limit)
            )

            predictions = result.scalars().all()

            logger.debug(
                f"Retrieved {len(predictions)} predictions for machine {machine_id}"
            )

            return predictions

        except Exception as e:
            logger.error(f"Database error retrieving machine predictions: {str(e)}")
            raise

    async def get_by_timerange(
        self, machine_id: int, start_time: str, end_time: str
    ) -> List[Prediction]:
        """Get predictions within time range for a machine.

        Args:
            machine_id: Machine identifier
            start_time: Start timestamp (ISO format string)
            end_time: End timestamp (ISO format string)

        Returns:
            List of Prediction objects within time range, ordered by created_at ascending
        """
        try:
            # Parse timestamps
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)

            result = await self.db.execute(
                select(Prediction)
                .where(
                    and_(
                        Prediction.machine_id == machine_id,
                        Prediction.created_at >= start_dt,
                        Prediction.created_at <= end_dt,
                    )
                )
                .order_by(Prediction.created_at.asc())
            )

            predictions = result.scalars().all()

            logger.debug(
                f"Retrieved {len(predictions)} predictions for machine {machine_id} "
                f"from {start_time} to {end_time}"
            )

            return predictions

        except ValueError as e:
            logger.error(f"Invalid timestamp format: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Database error retrieving predictions by timerange: {str(e)}")
            raise

    async def count(self, machine_id: int) -> int:
        """Count predictions for a machine.

        Args:
            machine_id: Machine identifier

        Returns:
            Number of predictions for the machine
        """
        try:
            result = await self.db.execute(
                select(func.count()).select_from(Prediction)
                .where(Prediction.machine_id == machine_id)
            )

            count = result.scalar_one()

            logger.debug(f"Machine {machine_id} has {count} predictions")

            return count

        except Exception as e:
            logger.error(f"Database error counting predictions: {str(e)}")
            raise

    async def exists(self, machine_id: int, timestamp: str) -> bool:
        """Check if prediction exists for machine at timestamp.

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
                select(func.count()).select_from(Prediction)
                .where(
                    and_(
                        Prediction.machine_id == machine_id,
                        Prediction.created_at == ts,
                    )
                )
            )

            count = result.scalar_one()
            exists = count > 0

            logger.debug(
                f"Prediction exists for machine {machine_id} at {timestamp}: {exists}"
            )

            return exists

        except ValueError as e:
            logger.error(f"Invalid timestamp format: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Database error checking prediction existence: {str(e)}")
            raise
