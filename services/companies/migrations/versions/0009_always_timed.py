"""every interview is timed, and candidates never see their scores

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("interviews", "share_results")
    op.drop_column("interviews", "timed")


def downgrade() -> None:
    op.add_column(
        "interviews",
        sa.Column("timed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "interviews",
        sa.Column("share_results", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
