"""extra time for a candidate who needs it, as a percentage of each question's time

Revision ID: 0021
Revises: 0020
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "candidate_invites",
        sa.Column("extra_time", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("candidate_invites", "extra_time")
