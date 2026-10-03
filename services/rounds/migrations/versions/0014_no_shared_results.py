"""candidates never see their interview scores

Revision ID: 0014
Revises: 0013
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("sessions", "share_results")


def downgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("share_results", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
