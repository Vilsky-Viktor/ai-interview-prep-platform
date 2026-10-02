"""timed interviews: whether an interview has a time limit, and how many minutes

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-02
"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interviews", sa.Column("timed", sa.Boolean(), nullable=False, server_default=sa.false())
    )
    op.add_column(
        "interviews",
        sa.Column("time_limit_minutes", sa.Integer(), nullable=False, server_default="60"),
    )


def downgrade() -> None:
    op.drop_column("interviews", "time_limit_minutes")
    op.drop_column("interviews", "timed")
