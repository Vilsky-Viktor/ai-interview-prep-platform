"""ats_candidates: how many invites failed in passing (tried again by the recovery job), and
the results kept while a connection is broken (sent once it's reconnected).

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ats_candidates",
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("ats_candidates", sa.Column("result", JSONB()))


def downgrade() -> None:
    op.drop_column("ats_candidates", "result")
    op.drop_column("ats_candidates", "attempts")
