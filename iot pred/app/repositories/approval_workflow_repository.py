"""Approval workflow repository for database operations."""

import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval_workflow import ApprovalWorkflow

logger = logging.getLogger(__name__)


class ApprovalWorkflowRepository:
    """Repository for approval workflow database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with async database session.

        Args:
            db: AsyncSession for database operations (dependency injected)
        """
        self.db = db

    async def create(self, workflow: ApprovalWorkflow) -> ApprovalWorkflow:
        """Create a new approval workflow.

        Args:
            workflow: ApprovalWorkflow ORM object with values set

        Returns:
            Created ApprovalWorkflow object with id and timestamps populated

        Raises:
            Exception: If database operation fails
        """
        try:
            self.db.add(workflow)
            await self.db.flush()
            await self.db.refresh(workflow)

            logger.info(
                f"Approval workflow created for maintenance {workflow.maintenance_id}"
            )
            return workflow

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error creating approval workflow: {str(e)}")
            raise

    async def get_by_id(self, workflow_id: int) -> Optional[ApprovalWorkflow]:
        """Get approval workflow by primary key.

        Args:
            workflow_id: ApprovalWorkflow primary key

        Returns:
            ApprovalWorkflow object or None if not found
        """
        try:
            result = await self.db.execute(
                select(ApprovalWorkflow).where(ApprovalWorkflow.id == workflow_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Database error retrieving approval workflow: {str(e)}")
            raise

    async def get_by_maintenance_id(
        self, maintenance_id: int
    ) -> Optional[ApprovalWorkflow]:
        """Get approval workflow by maintenance ID.

        Args:
            maintenance_id: Maintenance primary key

        Returns:
            ApprovalWorkflow object or None if not found
        """
        try:
            result = await self.db.execute(
                select(ApprovalWorkflow).where(
                    ApprovalWorkflow.maintenance_id == maintenance_id
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"Database error retrieving approval workflow for maintenance {maintenance_id}: {str(e)}"
            )
            raise

    async def get_all(self) -> List[ApprovalWorkflow]:
        """Get all approval workflows.

        Returns:
            List of all ApprovalWorkflow objects
        """
        try:
            result = await self.db.execute(
                select(ApprovalWorkflow).order_by(ApprovalWorkflow.id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Database error retrieving all approval workflows: {str(e)}")
            raise

    async def update(
        self,
        workflow_id: int,
        reviewed_by: Optional[int] = None,
        status: Optional[object] = None,
        review_comments: Optional[str] = None,
    ) -> Optional[ApprovalWorkflow]:
        """Update approval workflow details.

        Args:
            workflow_id: ApprovalWorkflow primary key
            reviewed_by: Reviewer user ID (if provided)
            status: Workflow status (if provided)
            review_comments: Review feedback (if provided)

        Returns:
            Updated ApprovalWorkflow object, None if not found

        Raises:
            Exception: If database operation fails
        """
        try:
            workflow = await self.get_by_id(workflow_id)
            if not workflow:
                return None

            if reviewed_by is not None:
                workflow.reviewed_by = reviewed_by
            if status is not None:
                workflow.status = status
            if review_comments is not None:
                workflow.review_comments = review_comments

            await self.db.commit()
            await self.db.refresh(workflow)

            logger.info(f"Approval workflow {workflow_id} updated")
            return workflow

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database error updating approval workflow: {str(e)}")
            raise
