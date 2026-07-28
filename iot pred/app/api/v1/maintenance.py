"""Maintenance API endpoints with role-based access control."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorization import Permission
from app.db.database import get_async_session
from app.dependencies.authorization import require_permission
from app.models.user import User
from app.schemas.maintenance import MaintenanceCreate, MaintenanceResponse, MaintenanceUpdate
from app.services.maintenance_service import MaintenanceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.get("", response_model=list[MaintenanceResponse])
async def list_maintenance(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.CREATE_MAINTENANCE)),
):
    """Get all maintenance records.

    Requires: CREATE_MAINTENANCE permission (Maintenance Engineer, Admin)

    Returns:
        HTTP 200 with list of maintenance records
        HTTP 403 if unauthorized
    """
    try:
        service = MaintenanceService(db)
        maintenance_records = await service.get_all_maintenance()
        logger.info(f"Listed {len(maintenance_records)} maintenance records by user {current_user.id}")
        return maintenance_records
    except Exception as e:
        logger.error(f"Error listing maintenance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve maintenance records",
        )


@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
async def get_maintenance(
    maintenance_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.CREATE_MAINTENANCE)),
):
    """Get maintenance record by ID.

    Requires: CREATE_MAINTENANCE permission (Maintenance Engineer, Admin)

    Args:
        maintenance_id: Maintenance primary key

    Returns:
        HTTP 200 with maintenance details
        HTTP 403 if unauthorized
        HTTP 404 if maintenance not found
    """
    try:
        service = MaintenanceService(db)
        maintenance = await service.get_maintenance(maintenance_id)

        if not maintenance:
            logger.warning(f"Maintenance {maintenance_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maintenance {maintenance_id} not found",
            )

        logger.info(f"Retrieved maintenance {maintenance_id} by user {current_user.id}")
        return maintenance
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving maintenance {maintenance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve maintenance",
        )


@router.get("/asset/{asset_id}", response_model=list[MaintenanceResponse])
async def get_asset_maintenance(
    asset_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.CREATE_MAINTENANCE)),
):
    """Get maintenance history for a specific asset.

    Requires: CREATE_MAINTENANCE permission (Maintenance Engineer, Admin)

    Args:
        asset_id: Asset primary key

    Returns:
        HTTP 200 with list of maintenance records for asset
        HTTP 403 if unauthorized
    """
    try:
        service = MaintenanceService(db)
        maintenance_records = await service.get_asset_maintenance(asset_id)
        logger.info(
            f"Retrieved {len(maintenance_records)} maintenance records for asset {asset_id} "
            f"by user {current_user.id}"
        )
        return maintenance_records
    except Exception as e:
        logger.error(f"Error retrieving maintenance for asset {asset_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve asset maintenance",
        )


@router.post("", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    maintenance_data: MaintenanceCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.CREATE_MAINTENANCE)),
):
    """Create a new maintenance record.

    Requires: CREATE_MAINTENANCE permission (Maintenance Engineer, Admin)

    Args:
        maintenance_data: Maintenance creation data

    Returns:
        HTTP 201 with created maintenance record
        HTTP 403 if unauthorized
        HTTP 500 if creation fails
    """
    try:
        service = MaintenanceService(db)
        new_maintenance = await service.create_maintenance(maintenance_data, current_user.id)
        logger.info(f"Maintenance created by user {current_user.id} for asset {maintenance_data.asset_id}")
        return new_maintenance
    except Exception as e:
        logger.error(f"Error creating maintenance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create maintenance",
        )


@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
async def update_maintenance(
    maintenance_id: int,
    maintenance_data: MaintenanceUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.UPDATE_MAINTENANCE)),
):
    """Update maintenance record details.

    Requires: UPDATE_MAINTENANCE permission (Maintenance Engineer, Admin)

    Args:
        maintenance_id: Maintenance primary key
        maintenance_data: Update data

    Returns:
        HTTP 200 with updated maintenance
        HTTP 403 if unauthorized
        HTTP 404 if maintenance not found
        HTTP 400 if invalid status transition
    """
    try:
        service = MaintenanceService(db)
        updated_maintenance = await service.update_maintenance(maintenance_id, maintenance_data)

        if not updated_maintenance:
            logger.warning(f"Maintenance {maintenance_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maintenance {maintenance_id} not found",
            )

        logger.info(f"Maintenance {maintenance_id} updated by user {current_user.id}")
        return updated_maintenance

    except ValueError as e:
        logger.warning(f"Maintenance update validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating maintenance {maintenance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update maintenance",
        )


@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance(
    maintenance_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.UPDATE_MAINTENANCE)),
):
    """Delete a maintenance record.

    Requires: UPDATE_MAINTENANCE permission (Maintenance Engineer, Admin)

    Args:
        maintenance_id: Maintenance primary key

    Returns:
        HTTP 204 No Content
        HTTP 403 if unauthorized
        HTTP 404 if maintenance not found
    """
    try:
        service = MaintenanceService(db)
        deleted = await service.delete_maintenance(maintenance_id)

        if not deleted:
            logger.warning(f"Maintenance {maintenance_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maintenance {maintenance_id} not found",
            )

        logger.info(f"Maintenance {maintenance_id} deleted by user {current_user.id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting maintenance {maintenance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete maintenance",
        )


@router.patch("/{maintenance_id}/start", response_model=MaintenanceResponse)
async def start_maintenance(
    maintenance_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.UPDATE_MAINTENANCE)),
):
    """Mark maintenance as in progress.

    Requires: UPDATE_MAINTENANCE permission (Maintenance Engineer, Admin)

    Args:
        maintenance_id: Maintenance primary key

    Returns:
        HTTP 200 with updated maintenance
        HTTP 403 if unauthorized
        HTTP 404 if maintenance not found
        HTTP 400 if invalid status transition
    """
    try:
        service = MaintenanceService(db)
        updated_maintenance = await service.mark_in_progress(maintenance_id)

        if not updated_maintenance:
            logger.warning(f"Maintenance {maintenance_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maintenance {maintenance_id} not found",
            )

        logger.info(f"Maintenance {maintenance_id} started by user {current_user.id}")
        return updated_maintenance

    except ValueError as e:
        logger.warning(f"Maintenance status transition failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting maintenance {maintenance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start maintenance",
        )


@router.patch("/{maintenance_id}/complete", response_model=MaintenanceResponse)
async def complete_maintenance(
    maintenance_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.UPDATE_MAINTENANCE)),
):
    """Mark maintenance as completed.

    Requires: UPDATE_MAINTENANCE permission (Maintenance Engineer, Admin)

    Args:
        maintenance_id: Maintenance primary key

    Returns:
        HTTP 200 with updated maintenance
        HTTP 403 if unauthorized
        HTTP 404 if maintenance not found
        HTTP 400 if invalid status transition
    """
    try:
        service = MaintenanceService(db)
        updated_maintenance = await service.mark_complete(maintenance_id)

        if not updated_maintenance:
            logger.warning(f"Maintenance {maintenance_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maintenance {maintenance_id} not found",
            )

        logger.info(f"Maintenance {maintenance_id} completed by user {current_user.id}")
        return updated_maintenance

    except ValueError as e:
        logger.warning(f"Maintenance status transition failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing maintenance {maintenance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete maintenance",
        )


@router.patch("/{maintenance_id}/cancel", response_model=MaintenanceResponse)
async def cancel_maintenance(
    maintenance_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_permission(Permission.UPDATE_MAINTENANCE)),
):
    """Mark maintenance as cancelled.

    Requires: UPDATE_MAINTENANCE permission (Maintenance Engineer, Admin)

    Args:
        maintenance_id: Maintenance primary key

    Returns:
        HTTP 200 with updated maintenance
        HTTP 403 if unauthorized
        HTTP 404 if maintenance not found
        HTTP 400 if invalid status transition
    """
    try:
        service = MaintenanceService(db)
        updated_maintenance = await service.mark_cancelled(maintenance_id)

        if not updated_maintenance:
            logger.warning(f"Maintenance {maintenance_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maintenance {maintenance_id} not found",
            )

        logger.info(f"Maintenance {maintenance_id} cancelled by user {current_user.id}")
        return updated_maintenance

    except ValueError as e:
        logger.warning(f"Maintenance status transition failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling maintenance {maintenance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel maintenance",
        )
