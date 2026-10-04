"""events received, so grouped notifications are still stored once per event

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "received",
        sa.Column("event_id", sa.String(128), primary_key=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_received_received_at", "received", ["received_at"])
    # Events stored before this table existed count as received.
    op.execute(
        "INSERT INTO received (event_id, received_at) SELECT event_id, created_at FROM notifications"
    )


def downgrade() -> None:
    op.drop_table("received")
