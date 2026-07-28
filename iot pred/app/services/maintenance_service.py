"""Maintenance service for maintenance record business logic."""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MaintenanceStatus
from app.models.maintenance import Maintenance
from app.repositories.maintenance_repository import MaintenanceRepository
from app.schemas.maintenance import MaintenanceCreate, MaintenanceResponse, MaintenanceUpdate

logger = logging.getLogger(__name__)


class MaintenanceService:
    """Service for maintenance record business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db
        self.repository = MaintenanceRepository(db)

    async def create_maintenance(self, maintenance_data: MaintenanceCreate, user_id: int) -> MaintenanceResponse:
        """Create a new maintenance record.

        Args:
            maintenance_data: MaintenanceCreate schema with maintenance details
            user_id: User ID of who created the record

        Returns:
            Created MaintenanceResponse object

        Raises:
            ValueError: If asset_id is invalid
            Exception: If database operation fails
        """
        try:
            maintenance = Maintenance(
                asset_id=maintenance_data.asset_id,
                created_by=user_id,
                maintenance_type=maintenance_data.maintenance_type,
                description=maintenance_data.description,
                status=maintenance_data.status,
                scheduled_date=maintenance_data.scheduled_date,
            )

            created_maintenance = await self.repository.create(maintenance)
            logger.info(
                f"Maintenance created by user {user_id} for asset {maintenance_data.asset_id}"
            )
            return MaintenanceResponse.model_validate(created_maintenance)

        except Exception as e:
            logger.error(f"Error creating maintenance: {str(e)}")
            raise

    async def get_maintenance(self, maintenance_id: int) -> Optional[MaintenanceResponse]:
        """Get maintenance record by ID.

        Args:
            maintenance_id: Maintenance primary key

        Returns:
            MaintenanceResponse if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            maintenance = await self.repository.get_by_id(maintenance_id)
            if not maintenance:
                logger.warning(f"Maintenance {maintenance_id} not found")
                return None

            logger.info(f"Retrieved maintenance {maintenance_id}")
            return MaintenanceResponse.model_validate(maintenance)

        except Exception as e:
            logger.error(f"Error retrieving maintenance {maintenance_id}: {str(e)}")
            raise

    async def get_all_maintenance(self) -> List[MaintenanceResponse]:
        """Get all maintenance records.

        Returns:
            List of MaintenanceResponse objects

        Raises:
            Exception: If database operation fails
        """
        try:
            maintenance_records = await self.repository.get_all()
            logger.info(f"Retrieved {len(maintenance_records)} maintenance records")
            return [
                MaintenanceResponse.model_validate(m) for m in maintenance_records
            ]

        except Exception as e:
            logger.error(f"Error retrieving all maintenance: {str(e)}")
            raise

    async def get_asset_maintenance(self, asset_id: int) -> List[MaintenanceResponse]:
        """Get all maintenance records for a specific asset.

        Args:
            asset_id: Asset primary key

        Returns:
            List of MaintenanceResponse objects for the asset

        Raises:
            Exception: If database operation fails
        """
        try:
            maintenance_records = await self.repository.get_by_asset_id(asset_id)
            logger.info(
                f"Retrieved {len(maintenance_records)} maintenance records for asset {asset_id}"
            )
            return [
                MaintenanceResponse.model_validate(m) for m in maintenance_records
            ]

        except Exception as e:
            logger.error(
                f"Error retrieving maintenance for asset {asset_id}: {str(e)}"
            )
            raise

    async def get_pending_maintenance(self) -> List[MaintenanceResponse]:
        """Get all pending maintenance records.

        Returns:
            List of MaintenanceResponse objects with PENDING status

        Raises:
            Exception: If database operation fails
        """
        try:
            maintenance_records = await self.repository.get_pending()
            logger.info(f"Retrieved {len(maintenance_records)} pending maintenance records")
            return [
                MaintenanceResponse.model_validate(m) for m in maintenance_records
            ]

        except Exception as e:
            logger.error(f"Error retrieving pending maintenance: {str(e)}")
            raise

    async def update_maintenance(
        self, maintenance_id: int, update_data: MaintenanceUpdate
    ) -> Optional[MaintenanceResponse]:
        """Update maintenance record details.

        Args:
            maintenance_id: Maintenance primary key
            update_data: MaintenanceUpdate schema with fields to update

        Returns:
            Updated MaintenanceResponse if successful, None if not found

        Raises:
            ValueError: If status transition is invalid
            Exception: If database operation fails
        """
        try:
            maintenance = await self.repository.get_by_id(maintenance_id)
            if not maintenance:
                logger.warning(f"Maintenance {maintenance_id} not found for update")
                return None

            # Validate status transitions if status is being changed
            if update_data.status and update_data.status != maintenance.status:
                self._validate_status_transition(maintenance.status, update_data.status)

            updated_maintenance = await self.repository.update(
                maintenance_id,
                maintenance_type=update_data.maintenance_type,
                description=update_data.description,
                status=update_data.status,
                scheduled_date=update_data.scheduled_date,
                completed_date=update_data.completed_date,
            )

            logger.info(f"Maintenance {maintenance_id} updated")
            return MaintenanceResponse.model_validate(updated_maintenance)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating maintenance {maintenance_id}: {str(e)}")
            raise

    async def delete_maintenance(self, maintenance_id: int) -> bool:
        """Delete a maintenance record.

        Args:
            maintenance_id: Maintenance primary key

        Returns:
            True if deleted, False if not found

        Raises:
            Exception: If database operation fails
        """
        try:
            deleted = await self.repository.delete(maintenance_id)
            if deleted:
                logger.info(f"Maintenance {maintenance_id} deleted")
            else:
                logger.warning(f"Maintenance {maintenance_id} not found for deletion")
            return deleted

        except Exception as e:
            logger.error(f"Error deleting maintenance {maintenance_id}: {str(e)}")
            raise

    async def mark_in_progress(self, maintenance_id: int) -> Optional[MaintenanceResponse]:
        """Mark maintenance as in progress.

        Args:
            maintenance_id: Maintenance primary key

        Returns:
            Updated MaintenanceResponse if successful, None if not found

        Raises:
            ValueError: If status transition is invalid
            Exception: If database operation fails
        """
        try:
            maintenance = await self.repository.get_by_id(maintenance_id)
            if not maintenance:
                logger.warning(f"Maintenance {maintenance_id} not found")
                return None

            self._validate_status_transition(
                maintenance.status, MaintenanceStatus.IN_PROGRESS
            )

            updated_maintenance = await self.repository.update(
                maintenance_id, status=MaintenanceStatus.IN_PROGRESS
            )

            logger.info(f"Maintenance {maintenance_id} marked as IN_PROGRESS")
            return MaintenanceResponse.model_validate(updated_maintenance)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error marking maintenance as in progress: {str(e)}")
            raise

    async def mark_complete(self, maintenance_id: int) -> Optional[MaintenanceResponse]:
        """Mark maintenance as completed.

        Args:
            maintenance_id: Maintenance primary key

        Returns:
            Updated MaintenanceResponse if successful, None if not found

        Raises:
            ValueError: If status transition is invalid
            Exception: If database operation fails
        """
        try:
            maintenance = await self.repository.get_by_id(maintenance_id)
            if not maintenance:
                logger.warning(f"Maintenance {maintenance_id} not found")
                return None

            self._validate_status_transition(
                maintenance.status, MaintenanceStatus.COMPLETED
            )

            updated_maintenance = await self.repository.update(
                maintenance_id,
                status=MaintenanceStatus.COMPLETED,
                completed_date=datetime.utcnow(),
            )

            logger.info(f"Maintenance {maintenance_id} marked as COMPLETED")
            return MaintenanceResponse.model_validate(updated_maintenance)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error marking maintenance as complete: {str(e)}")
            raise

    async def mark_cancelled(self, maintenance_id: int) -> Optional[MaintenanceResponse]:
        """Mark maintenance as cancelled.

        Args:
            maintenance_id: Maintenance primary key

        Returns:
            Updated MaintenanceResponse if successful, None if not found

        Raises:
            ValueError: If status transition is invalid
            Exception: If database operation fails
        """
        try:
            maintenance = await self.repository.get_by_id(maintenance_id)
            if not maintenance:
                logger.warning(f"Maintenance {maintenance_id} not found")
                return None

            self._validate_status_transition(
                maintenance.status, MaintenanceStatus.CANCELLED
            )

            updated_maintenance = await self.repository.update(
                maintenance_id, status=MaintenanceStatus.CANCELLED
            )

            logger.info(f"Maintenance {maintenance_id} marked as CANCELLED")
            return MaintenanceResponse.model_validate(updated_maintenance)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error marking maintenance as cancelled: {str(e)}")
            raise

    def _validate_status_transition(
        self, current_status: MaintenanceStatus, new_status: MaintenanceStatus
    ) -> None:
        """Validate if a status transition is allowed.

        Args:
            current_status: Current maintenance status
            new_status: Desired new status

        Raises:
            ValueError: If status transition is not allowed
        """
        valid_transitions = {
            MaintenanceStatus.PENDING: {
                MaintenanceStatus.SCHEDULED,
                MaintenanceStatus.CANCELLED,
            },
            MaintenanceStatus.SCHEDULED: {
                MaintenanceStatus.IN_PROGRESS,
                MaintenanceStatus.CANCELLED,
            },
            MaintenanceStatus.IN_PROGRESS: {
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.CANCELLED,
            },
            MaintenanceStatus.COMPLETED: set(),
            MaintenanceStatus.CANCELLED: set(),
        }

        allowed_statuses = valid_transitions.get(current_status, set())
        if new_status not in allowed_statuses:
            logger.warning(
                f"Invalid status transition: {current_status.value} → {new_status.value}"
            )
            raise ValueError(
                f"Cannot transition from {current_status.value} to {new_status.value}"
            )
