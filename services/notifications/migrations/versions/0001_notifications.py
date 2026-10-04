"""the bell's notifications, and when each user last opened it

Revision ID: 0001
Revises:
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("event_id", sa.String(128), nullable=False, unique=True),
        sa.Column("recipient", sa.String(16), nullable=False),
        sa.Column("recipient_id", sa.String(128), nullable=False),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("link", sa.Text(), nullable=False),
        sa.Column("data", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_notifications_recipient", "notifications", ["recipient", "recipient_id", "created_at"]
    )
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])
    op.create_table(
        "seen",
        sa.Column("user_id", sa.String(128), primary_key=True),
        sa.Column("seen_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("seen")
    op.drop_table("notifications")
