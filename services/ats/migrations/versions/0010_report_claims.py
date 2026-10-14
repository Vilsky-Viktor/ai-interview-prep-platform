"""ats_candidates report_claimed_at: results are marked as gone back only once the ATS took them,
so a write cut off midway is sent again

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ats_candidates", sa.Column("report_claimed_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("ats_candidates", "report_claimed_at")
