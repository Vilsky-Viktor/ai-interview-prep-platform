"""candidate_invites started_at and finished_at: when a candidate started and finished, for the
public API

Revision ID: 0044
Revises: 0043
Create Date: 2026-10-15
"""

import sqlalchemy as sa
from alembic import op

revision = "0044"
down_revision = "0043"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("candidate_invites", sa.Column("started_at", sa.DateTime(timezone=True)))
    op.add_column("candidate_invites", sa.Column("finished_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("candidate_invites", "finished_at")
    op.drop_column("candidate_invites", "started_at")
