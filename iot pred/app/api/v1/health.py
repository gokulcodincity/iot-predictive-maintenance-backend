"""Health check endpoints for production monitoring and orchestration."""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.db.database import get_database_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def get_health():
    """Check application health (liveness probe).

    This endpoint verifies that the application is running and responding.
    Used by Kubernetes, Docker, AWS ALB, and monitoring tools for liveness checks.

    Returns:
        HTTP 200 with health status dictionary:
            - status: "healthy" (always on success)
            - service: Service name and description
            - version: API version
            - timestamp: ISO UTC timestamp of check
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "Industrial IoT Predictive Maintenance Backend",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.debug("Application health check passed")
        return health_status

    except Exception as e:
        logger.error(f"Application health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application health check failed",
        )


@router.get("/database")
async def get_health_database():
    """Check database connectivity (readiness probe).

    This endpoint verifies that the application can connect to the database.
    Used by Kubernetes, Docker, AWS ALB, and monitoring tools for readiness checks.
    Critical for rolling deployments and load balancer health verification.

    Returns:
        HTTP 200 with database health status:
            - status: "healthy"
            - database: "connected"

        HTTP 503 (Service Unavailable) if database unreachable:
            - status: "unhealthy"
            - database: "disconnected"
            - error: Error message describing connection failure
    """
    try:
        db_manager = await get_database_manager()
        is_healthy = await db_manager.check_connection()

        if is_healthy:
            logger.debug("Database health check passed")
            return {
                "status": "healthy",
                "database": "connected",
            }
        else:
            logger.error("Database health check failed: connection unsuccessful")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": "Database connection failed",
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database health check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            },
        )
