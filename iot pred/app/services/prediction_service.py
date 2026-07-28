"""Prediction service for prediction operations."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundException
from app.models.prediction import Prediction
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.prediction import PredictionCreate


class PredictionService:
    """Service for prediction operations."""

    def __init__(self, db: AsyncSession):
        """Initialize prediction service with async database session."""
        self.db = db
        self.prediction_repository = PredictionRepository(db)

    async def create_prediction(self, prediction_data: PredictionCreate) -> Prediction:
        """Create a new prediction from AI inference results.

        Args:
            prediction_data: Prediction creation data from AI models

        Returns:
            Created Prediction object with id and timestamps
        """
        prediction = Prediction(
            machine_id=prediction_data.machine_id,
            telemetry_id=prediction_data.telemetry_id,
            anomaly_score=prediction_data.anomaly_score,
            failure_risk=prediction_data.failure_risk,
            confidence=prediction_data.confidence,
            prediction_status=prediction_data.prediction_status,
            model_version=prediction_data.model_version,
            inference_time_ms=prediction_data.inference_time_ms,
        )
        return await self.prediction_repository.create(prediction)

    async def get_prediction_by_id(self, prediction_id: int) -> Prediction:
        """Get prediction by id.

        Args:
            prediction_id: Prediction primary key

        Returns:
            Prediction object

        Raises:
            ResourceNotFoundException: If prediction not found
        """
        prediction = await self.prediction_repository.get_by_id(prediction_id)
        if not prediction:
            raise ResourceNotFoundException(
                f"Prediction with id {prediction_id} not found"
            )
        return prediction

    async def get_all_predictions(self) -> list[Prediction]:
        """Get all predictions.

        Returns:
            List of all Prediction objects
        """
        return await self.prediction_repository.get_all()

    async def get_latest_prediction(self, machine_id: int) -> Prediction:
        """Get latest prediction for a machine.

        Args:
            machine_id: Asset/machine primary key

        Returns:
            Latest Prediction object for the machine

        Raises:
            ResourceNotFoundException: If no predictions found for machine
        """
        prediction = await self.prediction_repository.get_latest_by_machine(
            machine_id
        )
        if not prediction:
            raise ResourceNotFoundException(
                f"No predictions found for machine {machine_id}"
            )
        return prediction

    async def get_machine_predictions(self, machine_id: int) -> list[Prediction]:
        """Get all predictions for a machine.

        Args:
            machine_id: Asset/machine primary key

        Returns:
            List of Prediction objects for the machine, newest first
        """
        return await self.prediction_repository.get_by_machine(machine_id)
