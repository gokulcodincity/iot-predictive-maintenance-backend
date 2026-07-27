"""Telemetry service for telemetry operations."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundException
from app.models.telemetry import Telemetry
from app.repositories.telemetry_repository import TelemetryRepository
from app.schemas.telemetry import TelemetryCreate


class TelemetryService:
    """Service for telemetry operations."""

    def __init__(self, db: AsyncSession):
        """Initialize telemetry service with async database session."""
        self.db = db
        self.telemetry_repository = TelemetryRepository(db)

    async def create_telemetry(self, telemetry_data: TelemetryCreate) -> Telemetry:
        """Create a new telemetry reading.

        Args:
            telemetry_data: Telemetry creation data from request

        Returns:
            Created Telemetry object with id and timestamps
        """
        telemetry = Telemetry(
            machine_id=telemetry_data.machine_id,
            temperature=telemetry_data.temperature,
            vibration=telemetry_data.vibration,
            current=telemetry_data.current,
            speed=telemetry_data.speed,
            throughput=telemetry_data.throughput,
            timestamp=telemetry_data.timestamp,
        )
        return await self.telemetry_repository.create(telemetry)

    async def get_telemetry_by_id(self, telemetry_id: int) -> Telemetry:
        """Get telemetry reading by id.

        Args:
            telemetry_id: Telemetry primary key

        Returns:
            Telemetry object

        Raises:
            ResourceNotFoundException: If telemetry not found
        """
        telemetry = await self.telemetry_repository.get_by_id(telemetry_id)
        if not telemetry:
            raise ResourceNotFoundException(
                f"Telemetry with id {telemetry_id} not found"
            )
        return telemetry

    async def get_all_telemetry(self) -> list[Telemetry]:
        """Get all telemetry records.

        Returns:
            List of all Telemetry objects
        """
        return await self.telemetry_repository.get_all()

    async def get_latest_telemetry(self, machine_id: int) -> Telemetry:
        """Get latest telemetry reading for a machine.

        Args:
            machine_id: Asset/machine primary key

        Returns:
            Latest Telemetry object

        Raises:
            ResourceNotFoundException: If no telemetry found for machine
        """
        telemetry = await self.telemetry_repository.get_latest_by_machine(
            machine_id
        )
        if not telemetry:
            raise ResourceNotFoundException(
                f"No telemetry found for machine {machine_id}"
            )
        return telemetry

    async def get_machine_telemetry(self, machine_id: int) -> list[Telemetry]:
        """Get all telemetry readings for a machine.

        Args:
            machine_id: Asset/machine primary key

        Returns:
            List of Telemetry objects for the machine, newest first
        """
        return await self.telemetry_repository.get_by_machine(machine_id)
