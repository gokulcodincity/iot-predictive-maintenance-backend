"""Maintenance repository for database operations."""

import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MaintenanceStatus
from app.models.maintenance import Maintenance

logger = logging.getLogger(__name__)


class MaintenanceRepository:
    """Repository for maintenance record database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with async database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db

    async def create(self, maintenance: Maintenance) -> Maintenance:
        """Create a new maintenance record.

        Args:
            maintenance: Maintenance ORM object with values set

        Returns:
            Created Maintenance object with id and timestamps populated

        Raises:
            Exception: If database operation fails
        """
        try:
            self.db.add(maintenance)
            await self.db.flush()
            await self.db.refresh(maintenance)

            logger.info(
                f"Maintenance created for asset {maintenance.asset_id} "
                f"(type={maintenance.maintenance_type})"
            )
            return maintenance

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error creating maintenance: {str(e)}")
            raise

    async def get_by_id(self, maintenance_id: int) -> Optional[Maintenance]:
        """Get maintenance record by primary key.

        Args:
            maintenance_id: Maintenance primary key

        Returns:
            Maintenance object or None if not found
        """
        try:
            result = await self.db.execute(
                select(Maintenance).where(Maintenance.id == maintenance_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Database error retrieving maintenance: {str(e)}")
            raise

    async def get_all(self) -> List[Maintenance]:
        """Get all maintenance records.

        Returns:
            List of all Maintenance objects
        """
        try:
            result = await self.db.execute(
                select(Maintenance).order_by(Maintenance.id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Database error retrieving all maintenance: {str(e)}")
            raise

    async def get_by_asset_id(self, asset_id: int) -> List[Maintenance]:
        """Get all maintenance records for a specific asset.

        Args:
            asset_id: Asset primary key

        Returns:
            List of Maintenance objects for the asset
        """
        try:
            result = await self.db.execute(
                select(Maintenance)
                .where(Maintenance.asset_id == asset_id)
                .order_by(Maintenance.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(
                f"Database error retrieving maintenance for asset {asset_id}: {str(e)}"
            )
            raise

    async def get_pending(self) -> List[Maintenance]:
        """Get all pending maintenance records.

        Returns:
            List of Maintenance objects with PENDING status
        """
        try:
            result = await self.db.execute(
                select(Maintenance)
                .where(Maintenance.status == MaintenanceStatus.PENDING)
                .order_by(Maintenance.created_at)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Database error retrieving pending maintenance: {str(e)}")
            raise

    async def update(
        self,
        maintenance_id: int,
        maintenance_type: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[MaintenanceStatus] = None,
        scheduled_date: Optional[object] = None,
        completed_date: Optional[object] = None,
    ) -> Optional[Maintenance]:
        """Update maintenance record details.

        Args:
            maintenance_id: Maintenance primary key
            maintenance_type: New maintenance type (if provided)
            description: New description (if provided)
            status: New status (if provided)
            scheduled_date: New scheduled date (if provided)
            completed_date: New completed date (if provided)

        Returns:
            Updated Maintenance object, None if not found

        Raises:
            Exception: If database operation fails
        """
        try:
            maintenance = await self.get_by_id(maintenance_id)
            if not maintenance:
                return None

            if maintenance_type is not None:
                maintenance.maintenance_type = maintenance_type
            if description is not None:
                maintenance.description = description
            if status is not None:
                maintenance.status = status
            if scheduled_date is not None:
                maintenance.scheduled_date = scheduled_date
            if completed_date is not None:
                maintenance.completed_date = completed_date

            await self.db.commit()
            await self.db.refresh(maintenance)

            logger.info(f"Maintenance {maintenance_id} updated")
            return maintenance

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error updating maintenance: {str(e)}")
            raise

    async def delete(self, maintenance_id: int) -> bool:
        """Delete a maintenance record.

        Args:
            maintenance_id: Maintenance primary key

        Returns:
            True if deleted, False if not found

        Raises:
            Exception: If database operation fails
        """
        try:
            maintenance = await self.get_by_id(maintenance_id)
            if not maintenance:
                return False

            await self.db.delete(maintenance)
            await self.db.commit()

            logger.info(f"Maintenance {maintenance_id} deleted")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error deleting maintenance: {str(e)}")
            raise
