"""interview ready_at: when an interview got its questions, so a reminder to invite candidates
can count from it; interviews already ready count from when they were made

Revision ID: 0033
Revises: 0032
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0033"
down_revision = "0032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("interviews", sa.Column("ready_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE interviews SET ready_at = created_at WHERE set_id IS NOT NULL")


def downgrade() -> None:
    op.drop_column("interviews", "ready_at")
