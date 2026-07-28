"""Repository for telemetry database operations."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telemetry import Telemetry

logger = logging.getLogger(__name__)


class TelemetryRepository:
    """Repository for telemetry data persistence layer."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with async database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db

    async def save_telemetry(self, payload: dict) -> Telemetry:
        """Save telemetry record to database from payload.

        Args:
            payload: Dictionary with telemetry data:
                - machine_id: int
                - timestamp: str (ISO format)
                - temperature: float
                - vibration: float
                - current: float
                - speed: float
                - throughput: float

        Returns:
            Created Telemetry object with id and timestamps

        Raises:
            ValueError: If payload is invalid
            Exception: If database operation fails
        """
        try:
            # Validate required fields
            required_fields = {
                "machine_id",
                "timestamp",
                "temperature",
                "vibration",
                "current",
                "speed",
                "throughput",
            }
            missing_fields = required_fields - set(payload.keys())
            if missing_fields:
                raise ValueError(
                    f"Payload missing required fields: {', '.join(sorted(missing_fields))}"
                )

            # Create telemetry record
            telemetry = Telemetry(
                machine_id=payload["machine_id"],
                timestamp=payload["timestamp"],
                temperature=payload["temperature"],
                vibration=payload["vibration"],
                current=payload["current"],
                speed=payload["speed"],
                throughput=payload["throughput"],
            )

            # Add to session and flush (writes to DB)
            self.db.add(telemetry)
            await self.db.flush()

            logger.info(
                f"Telemetry saved for machine {payload['machine_id']} "
                f"at {payload['timestamp']}"
            )

            return telemetry

        except ValueError as e:
            await self.db.rollback()
            logger.error(f"Validation error saving telemetry: {str(e)}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error saving telemetry: {str(e)}")
            raise

    async def create(self, telemetry: Telemetry) -> Telemetry:
        """Create a new telemetry record (ORM object).

        Args:
            telemetry: Telemetry ORM object with values set

        Returns:
            Created Telemetry object with id and timestamps populated
        """
        try:
            self.db.add(telemetry)
            await self.db.flush()
            await self.db.refresh(telemetry)
            logger.info(f"Telemetry created for machine {telemetry.machine_id}")
            return telemetry
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error creating telemetry: {str(e)}")
            raise

    async def get_by_id(self, telemetry_id: int) -> Optional[Telemetry]:
        """Get telemetry record by primary key.

        Args:
            telemetry_id: Telemetry primary key

        Returns:
            Telemetry object or None if not found
        """
        try:
            result = await self.db.execute(
                select(Telemetry).where(Telemetry.id == telemetry_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Database error retrieving telemetry by id: {str(e)}")
            raise

    async def get_all(self) -> List[Telemetry]:
        """Get all telemetry records.

        Returns:
            List of all Telemetry objects
        """
        try:
            result = await self.db.execute(select(Telemetry))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Database error retrieving all telemetry: {str(e)}")
            raise

    async def get_latest(self, machine_id: int) -> Optional[Telemetry]:
        """Get most recent telemetry record for a machine.

        Args:
            machine_id: Machine identifier

        Returns:
            Latest Telemetry record or None if not found
        """
        try:
            result = await self.db.execute(
                select(Telemetry)
                .where(Telemetry.machine_id == machine_id)
                .order_by(Telemetry.timestamp.desc())
                .limit(1)
            )

            telemetry = result.scalar_one_or_none()

            if telemetry:
                logger.debug(f"Retrieved latest telemetry for machine {machine_id}")
            else:
                logger.debug(f"No telemetry found for machine {machine_id}")

            return telemetry

        except Exception as e:
            logger.error(f"Database error retrieving latest telemetry: {str(e)}")
            raise

    async def get_latest_by_machine(self, machine_id: int) -> Optional[Telemetry]:
        """Get most recent telemetry reading for a machine (legacy method).

        Args:
            machine_id: Asset/machine primary key

        Returns:
            Latest Telemetry object for the machine or None
        """
        return await self.get_latest(machine_id)

    async def get_by_machine(
        self, machine_id: int, limit: int = 100
    ) -> List[Telemetry]:
        """Get telemetry records for a machine (newest first).

        Args:
            machine_id: Machine identifier
            limit: Maximum number of records to return (default 100)

        Returns:
            List of Telemetry records ordered by timestamp descending
        """
        try:
            result = await self.db.execute(
                select(Telemetry)
                .where(Telemetry.machine_id == machine_id)
                .order_by(Telemetry.timestamp.desc())
                .limit(limit)
            )

            telemetry_records = result.scalars().all()

            logger.debug(
                f"Retrieved {len(telemetry_records)} telemetry records for machine {machine_id}"
            )

            return telemetry_records

        except Exception as e:
            logger.error(f"Database error retrieving machine telemetry: {str(e)}")
            raise

    async def get_by_timerange(
        self, machine_id: int, start_time: str, end_time: str
    ) -> List[Telemetry]:
        """Get telemetry records within time range for a machine.

        Args:
            machine_id: Machine identifier
            start_time: Start timestamp (ISO format string)
            end_time: End timestamp (ISO format string)

        Returns:
            List of Telemetry records within time range, ordered by timestamp ascending
        """
        try:
            # Parse timestamps
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)

            result = await self.db.execute(
                select(Telemetry)
                .where(
                    and_(
                        Telemetry.machine_id == machine_id,
                        Telemetry.timestamp >= start_dt,
                        Telemetry.timestamp <= end_dt,
                    )
                )
                .order_by(Telemetry.timestamp.asc())
            )

            telemetry_records = result.scalars().all()

            logger.debug(
                f"Retrieved {len(telemetry_records)} telemetry records for machine {machine_id} "
                f"from {start_time} to {end_time}"
            )

            return telemetry_records

        except ValueError as e:
            logger.error(f"Invalid timestamp format: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Database error retrieving telemetry by timerange: {str(e)}")
            raise

    async def delete_old(self, days: int) -> int:
        """Delete telemetry records older than specified days.

        Args:
            days: Number of days to retain (delete records older than this)

        Returns:
            Number of records deleted

        Raises:
            ValueError: If days is not positive
        """
        try:
            if days <= 0:
                raise ValueError("days must be greater than 0")

            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Get records to delete
            result = await self.db.execute(
                select(Telemetry).where(Telemetry.timestamp < cutoff_date)
            )

            old_records = result.scalars().all()
            count = len(old_records)

            # Delete each record
            for record in old_records:
                await self.db.delete(record)

            logger.info(f"Deleted {count} telemetry records older than {days} days")

            return count

        except ValueError as e:
            logger.error(f"Validation error deleting old telemetry: {str(e)}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error deleting old telemetry: {str(e)}")
            raise

    async def count(self, machine_id: int) -> int:
        """Count telemetry records for a machine.

        Args:
            machine_id: Machine identifier

        Returns:
            Number of telemetry records for the machine
        """
        try:
            result = await self.db.execute(
                select(func.count()).select_from(Telemetry)
                .where(Telemetry.machine_id == machine_id)
            )

            count = result.scalar_one()

            logger.debug(f"Machine {machine_id} has {count} telemetry records")

            return count

        except Exception as e:
            logger.error(f"Database error counting telemetry: {str(e)}")
            raise

    async def exists(self, machine_id: int, timestamp: str) -> bool:
        """Check if telemetry record exists for machine at timestamp.

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
                select(func.count()).select_from(Telemetry)
                .where(
                    and_(
                        Telemetry.machine_id == machine_id,
                        Telemetry.timestamp == ts,
                    )
                )
            )

            count = result.scalar_one()
            exists = count > 0

            logger.debug(
                f"Telemetry exists for machine {machine_id} at {timestamp}: {exists}"
            )

            return exists

        except ValueError as e:
            logger.error(f"Invalid timestamp format: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Database error checking telemetry existence: {str(e)}")
            raise
