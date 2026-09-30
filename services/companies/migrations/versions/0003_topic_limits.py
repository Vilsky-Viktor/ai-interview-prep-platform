"""per-topic question limits

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-30
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interviews",
        sa.Column("topic_limits", JSONB, nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("interviews", "topic_limits")
