"""invite reminders: when a candidate who hasn't started was reminded

Revision ID: 0017
Revises: 0016
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "candidate_invites",
        sa.Column("reminded_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("candidate_invites", "reminded_at")
