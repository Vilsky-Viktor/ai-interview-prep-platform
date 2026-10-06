"""outbox attempts: an event Pub/Sub keeps refusing is parked instead of blocking the rest

Revision ID: 0022
Revises: 0021
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("outbox", sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("outbox", "attempts")
