"""timed interviews limit each question in seconds instead of the whole interview in minutes

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-02
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("interviews", "time_limit_minutes")
    op.add_column(
        "interviews",
        sa.Column("question_seconds", sa.Integer(), nullable=False, server_default="60"),
    )


def downgrade() -> None:
    op.drop_column("interviews", "question_seconds")
    op.add_column(
        "interviews",
        sa.Column("time_limit_minutes", sa.Integer(), nullable=False, server_default="60"),
    )
