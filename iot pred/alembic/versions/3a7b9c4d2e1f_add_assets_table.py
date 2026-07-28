"""add_assets_table

Revision ID: 3a7b9c4d2e1f
Revises: 025e1d305878
Create Date: 2026-07-27 20:15:30.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a7b9c4d2e1f'
down_revision = '025e1d305878'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This migration is a no-op.
    # The old assets table schema was replaced by migration 65fbd450774e
    # with the correct column names and structure.
    # This migration exists only in the history to reconcile the branched migrations.
    pass


def downgrade() -> None:
    # No-op downgrade
    pass
