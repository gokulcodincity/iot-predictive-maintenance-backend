"""Prediction API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.prediction import PredictionCreate, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    prediction_data: PredictionCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new prediction from AI inference results.

    Returns:
        HTTP 201 with created prediction record
    """
    service = PredictionService(db)
    return await service.create_prediction(prediction_data)


@router.get("/machine/{machine_id}/latest", response_model=PredictionResponse)
async def get_latest_prediction(machine_id: int, db: AsyncSession = Depends(get_db)):
    """Get the latest prediction for a specific machine.

    Args:
        machine_id: Asset/machine primary key

    Returns:
        HTTP 200 with latest prediction
        HTTP 404 if no predictions found for machine
    """
    service = PredictionService(db)
    return await service.get_latest_prediction(machine_id)


@router.get("/machine/{machine_id}", response_model=list[PredictionResponse])
async def get_machine_predictions(
    machine_id: int, db: AsyncSession = Depends(get_db)
):
    """Get all predictions for a specific machine.

    Args:
        machine_id: Asset/machine primary key

    Returns:
        HTTP 200 with list of predictions (newest first)
    """
    service = PredictionService(db)
    return await service.get_machine_predictions(machine_id)


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(prediction_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific prediction by id.

    Args:
        prediction_id: Prediction primary key

    Returns:
        HTTP 200 with prediction
        HTTP 404 if not found
    """
    service = PredictionService(db)
    return await service.get_prediction_by_id(prediction_id)


@router.get("", response_model=list[PredictionResponse])
async def list_predictions(db: AsyncSession = Depends(get_db)):
    """Get all predictions.

    Returns:
        HTTP 200 with list of all predictions
    """
    service = PredictionService(db)
    return await service.get_all_predictions()
