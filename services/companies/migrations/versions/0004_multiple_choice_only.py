"""multiple choice only: interviews no longer have a mode

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("interviews", "mode")


def downgrade() -> None:
    op.add_column(
        "interviews", sa.Column("mode", sa.String(32), nullable=False, server_default="choice")
    )
