"""Approval workflow model for tracking maintenance review and approval process."""

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import ApprovalStatus
from app.models.base import BaseModel


class ApprovalWorkflow(BaseModel):
    """Approval workflow model for tracking maintenance review process."""

    __tablename__ = "approval_workflows"
    __allow_unmapped__ = True

    maintenance_id: Mapped[int] = mapped_column(
        ForeignKey("maintenance_records.id"), nullable=False, index=True, unique=True
    )
    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False
    )
    review_comments: Mapped[str | None] = mapped_column(Text, nullable=True)
