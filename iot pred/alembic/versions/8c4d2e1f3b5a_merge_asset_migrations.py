"""merge asset migrations

Revision ID: 8c4d2e1f3b5a
Revises: 3a7b9c4d2e1f, 65fbd450774e
Create Date: 2026-07-28 14:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c4d2e1f3b5a'
down_revision = ('3a7b9c4d2e1f', '65fbd450774e')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Merge migration: no database changes
    # This migration reconciles the two divergent asset table migrations
    pass


def downgrade() -> None:
    # Merge migration: no database changes to revert
    pass
