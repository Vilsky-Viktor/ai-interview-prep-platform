"""candidate_invites return_url and guest: where a company's own platform takes the candidate
back once they've finished, and whether its link opens the interview without signing in (invited
through the API)

Revision ID: 0042
Revises: 0041
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0042"
down_revision = "0041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("candidate_invites", sa.Column("return_url", sa.String(2048)))
    op.add_column(
        "candidate_invites",
        sa.Column("guest", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("candidate_invites", "guest")
    op.drop_column("candidate_invites", "return_url")
