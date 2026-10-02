"""seconds each interview answer took

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-02
"""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions", sa.Column("question_shown_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("answers", sa.Column("seconds", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("answers", "seconds")
    op.drop_column("sessions", "question_shown_at")
