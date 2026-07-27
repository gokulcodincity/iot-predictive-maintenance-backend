"""Telemetry repository for database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telemetry import Telemetry


class TelemetryRepository:
    """Repository for telemetry database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with async database session."""
        self.db = db

    async def create(self, telemetry: Telemetry) -> Telemetry:
        """Create a new telemetry record.

        Args:
            telemetry: Telemetry ORM object with values set

        Returns:
            Created Telemetry object with id and timestamps populated
        """
        self.db.add(telemetry)
        await self.db.commit()
        await self.db.refresh(telemetry)
        return telemetry

    async def get_by_id(self, telemetry_id: int):
        """Get telemetry record by primary key.

        Args:
            telemetry_id: Telemetry primary key

        Returns:
            Telemetry object or None if not found
        """
        result = await self.db.execute(
            select(Telemetry).filter(Telemetry.id == telemetry_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self):
        """Get all telemetry records.

        Returns:
            List of all Telemetry objects
        """
        result = await self.db.execute(select(Telemetry))
        return result.scalars().all()

    async def get_latest_by_machine(self, machine_id: int):
        """Get most recent telemetry reading for a machine.

        Args:
            machine_id: Asset/machine primary key

        Returns:
            Latest Telemetry object for the machine or None
        """
        result = await self.db.execute(
            select(Telemetry)
            .filter(Telemetry.machine_id == machine_id)
            .order_by(Telemetry.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_machine(self, machine_id: int):
        """Get all telemetry records for a specific machine.

        Args:
            machine_id: Asset/machine primary key

        Returns:
            List of Telemetry objects for the machine, ordered by timestamp descending
        """
        result = await self.db.execute(
            select(Telemetry)
            .filter(Telemetry.machine_id == machine_id)
            .order_by(Telemetry.timestamp.desc())
        )
        return result.scalars().all()
