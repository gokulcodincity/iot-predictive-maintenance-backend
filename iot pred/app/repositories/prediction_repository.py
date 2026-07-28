"""Prediction repository for database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction


class PredictionRepository:
    """Repository for prediction database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with async database session."""
        self.db = db

    async def create(self, prediction: Prediction) -> Prediction:
        """Create a new prediction record.

        Args:
            prediction: Prediction ORM object with values set

        Returns:
            Created Prediction object with id and created_at populated
        """
        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction)
        return prediction

    async def get_by_id(self, prediction_id: int):
        """Get prediction record by primary key.

        Args:
            prediction_id: Prediction primary key

        Returns:
            Prediction object or None if not found
        """
        result = await self.db.execute(
            select(Prediction).filter(Prediction.id == prediction_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self):
        """Get all prediction records.

        Returns:
            List of all Prediction objects
        """
        result = await self.db.execute(select(Prediction))
        return result.scalars().all()

    async def get_latest_by_machine(self, machine_id: int):
        """Get most recent prediction for a machine.

        Args:
            machine_id: Asset/machine primary key

        Returns:
            Latest Prediction object for the machine or None
        """
        result = await self.db.execute(
            select(Prediction)
            .filter(Prediction.machine_id == machine_id)
            .order_by(Prediction.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_machine(self, machine_id: int):
        """Get all predictions for a specific machine.

        Args:
            machine_id: Asset/machine primary key

        Returns:
            List of Prediction objects for the machine, ordered by created_at descending
        """
        result = await self.db.execute(
            select(Prediction)
            .filter(Prediction.machine_id == machine_id)
            .order_by(Prediction.created_at.desc())
        )
        return result.scalars().all()
