"""outbox: how often Pub/Sub refused each event, so one it won't take is parked

Revision ID: 0020
Revises: 0019
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("outbox", sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("outbox", "attempts")
