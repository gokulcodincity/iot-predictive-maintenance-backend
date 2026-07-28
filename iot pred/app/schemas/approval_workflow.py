"""Approval workflow schemas for request and response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import ApprovalStatus


class ApprovalWorkflowCreate(BaseModel):
    """Schema for creating a new approval workflow."""

    maintenance_id: int = Field(gt=0, description="Maintenance record ID to review")
    status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING, description="Initial status"
    )


class ApprovalWorkflowUpdate(BaseModel):
    """Schema for updating an approval workflow."""

    reviewed_by: int | None = Field(
        default=None, description="User ID of reviewer (Plant Manager)"
    )
    status: ApprovalStatus | None = Field(
        default=None, description="Workflow status"
    )
    review_comments: str | None = Field(
        default=None, description="Reviewer comments or feedback"
    )


class ApprovalWorkflowResponse(BaseModel):
    """Schema for approval workflow response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    maintenance_id: int
    reviewed_by: int | None
    status: ApprovalStatus
    review_comments: str | None
    created_at: datetime
    updated_at: datetime
