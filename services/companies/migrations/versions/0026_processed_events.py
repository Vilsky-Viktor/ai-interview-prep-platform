"""processed events: a redelivered event doesn't notify the company twice

Revision ID: 0026
Revises: 0025
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "processed_events",
        sa.Column("event_id", sa.String(128), primary_key=True),
        sa.Column(
            "received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_processed_events_received_at", "processed_events", ["received_at"])


def downgrade() -> None:
    op.drop_index("ix_processed_events_received_at", table_name="processed_events")
    op.drop_table("processed_events")
