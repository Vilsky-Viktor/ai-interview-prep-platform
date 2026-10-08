"""api: events a web hook didn't take, sent again by the retry job, and web hooks that kept
failing.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "webhooks",
        sa.Column("failing", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "webhook_retries",
        sa.Column(
            "webhook_id",
            sa.Uuid(),
            sa.ForeignKey("webhooks.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("event_id", sa.String(128), primary_key=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("next_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_webhook_retries_next_at", "webhook_retries", ["next_at"])


def downgrade() -> None:
    op.drop_table("webhook_retries")
    op.drop_column("webhooks", "failing")
