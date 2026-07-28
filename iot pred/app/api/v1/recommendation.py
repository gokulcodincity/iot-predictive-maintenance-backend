"""Recommendation API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendation", tags=["Recommendation"])


@router.get("/{machine_id}")
async def get_recommendation(
    machine_id: int, db: AsyncSession = Depends(get_async_session)
):
    """Get operator recommendation for a machine.

    Generates a structured recommendation based on latest prediction and alert data.
    Includes suggested action, severity level, and risk metrics.

    Args:
        machine_id: Machine identifier

    Returns:
        HTTP 200 with recommendation dictionary:
            - machine_id: Target machine
            - recommendation: Text guidance for operator
            - recommended_action: Action code (IMMEDIATE_SHUTDOWN, URGENT_MAINTENANCE, etc.)
            - severity: Alert severity level
            - failure_risk: Probability of equipment failure (0-1)
            - anomaly_score: Magnitude of detected anomaly (0-1)
            - generated_at: ISO UTC timestamp

    Raises:
        HTTP 500: If recommendation generation fails
    """
    try:
        service = RecommendationService(db)
        recommendation = await service.get_recommendation(machine_id)

        logger.info(
            f"Recommendation generated for machine {machine_id}: "
            f"action={recommendation.get('recommended_action')}"
        )
        return recommendation

    except Exception as e:
        logger.error(f"Error generating recommendation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendation",
        )
