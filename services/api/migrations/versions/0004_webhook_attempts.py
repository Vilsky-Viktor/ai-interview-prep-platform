"""api: webhook_attempts, each web hook's latest sends and how they went, for its delivery log

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-15
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "webhook_attempts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "webhook_id",
            sa.Uuid(),
            sa.ForeignKey("webhooks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_id", sa.String(128), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("ok", sa.Boolean(), nullable=False),
        sa.Column("result", sa.String(64), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_webhook_attempts_webhook_id", "webhook_attempts", ["webhook_id"])


def downgrade() -> None:
    op.drop_table("webhook_attempts")
