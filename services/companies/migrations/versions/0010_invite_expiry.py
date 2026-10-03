"""when an invite was last sent, so one never started can expire

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "candidate_invites",
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute("UPDATE candidate_invites SET sent_at = created_at")
    op.alter_column("candidate_invites", "sent_at", nullable=False)


def downgrade() -> None:
    op.drop_column("candidate_invites", "sent_at")
