"""Prediction API endpoints."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.prediction import PredictionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prediction", tags=["Prediction"])


@router.get("/latest/{machine_id}", response_model=PredictionResponse)
async def get_latest_prediction(
    machine_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Get the latest prediction for a machine.

    Args:
        machine_id: Machine identifier

    Returns:
        HTTP 200 with latest prediction record
        HTTP 404 if no prediction found for machine
    """
    try:
        repo = PredictionRepository(db)
        prediction = await repo.get_latest_by_machine(machine_id)

        if not prediction:
            logger.warning(f"No prediction found for machine {machine_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No prediction found for machine {machine_id}",
            )

        logger.info(f"Retrieved latest prediction for machine {machine_id}")
        return prediction

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction",
        )


@router.get("/history/{machine_id}", response_model=list[PredictionResponse])
async def get_prediction_history(
    machine_id: int,
    limit: int = Query(100, ge=1, le=10000),
    db: AsyncSession = Depends(get_async_session),
):
    """Get prediction history for a machine (newest first).

    Args:
        machine_id: Machine identifier
        limit: Maximum number of records (default 100, max 10000)

    Returns:
        HTTP 200 with list of prediction records
    """
    try:
        repo = PredictionRepository(db)
        predictions = await repo.get_by_machine(machine_id)

        # Apply limit
        predictions = predictions[:limit]

        logger.info(f"Retrieved {len(predictions)} predictions for machine {machine_id}")
        return predictions

    except Exception as e:
        logger.error(f"Error retrieving prediction history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction history",
        )


@router.get("/count/{machine_id}", response_model=dict)
async def get_prediction_count(
    machine_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Get total prediction count for a machine.

    Args:
        machine_id: Machine identifier

    Returns:
        HTTP 200 with count dictionary
    """
    try:
        repo = PredictionRepository(db)
        predictions = await repo.get_by_machine(machine_id)
        count = len(predictions)

        logger.info(f"Machine {machine_id} has {count} predictions")
        return {"machine_id": machine_id, "count": count}

    except Exception as e:
        logger.error(f"Error counting predictions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count predictions",
        )


@router.get("/range/{machine_id}", response_model=list[PredictionResponse])
async def get_prediction_range(
    machine_id: int,
    start_time: str = Query(..., description="Start timestamp (ISO format)"),
    end_time: str = Query(..., description="End timestamp (ISO format)"),
    db: AsyncSession = Depends(get_async_session),
):
    """Get predictions within a time range for a machine.

    Args:
        machine_id: Machine identifier
        start_time: Start timestamp (ISO format, e.g., 2026-07-28T00:00:00)
        end_time: End timestamp (ISO format, e.g., 2026-07-28T23:59:59)

    Returns:
        HTTP 200 with list of predictions within time range
    """
    try:
        # Validate timestamp format
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
        except ValueError as e:
            logger.error(f"Invalid timestamp format: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid timestamp format: {str(e)}",
            )

        repo = PredictionRepository(db)
        predictions = await repo.get_by_machine(machine_id)

        # Filter by time range
        predictions_in_range = [
            p for p in predictions
            if start_dt <= p.created_at <= end_dt
        ]

        logger.info(
            f"Retrieved {len(predictions_in_range)} predictions for machine {machine_id} "
            f"from {start_time} to {end_time}"
        )
        return predictions_in_range

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving prediction range: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction range",
        )
