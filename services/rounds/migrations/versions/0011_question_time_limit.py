"""timed interviews limit each question; integrity signals; answers can time out

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-02
"""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("sessions", "deadline")
    op.add_column("sessions", sa.Column("question_seconds", sa.Integer(), nullable=True))
    op.add_column(
        "sessions", sa.Column("tab_leaves", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column("sessions", sa.Column("copies", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("answers", "option_index", nullable=True)


def downgrade() -> None:
    op.execute("DELETE FROM answers WHERE option_index IS NULL")
    op.alter_column("answers", "option_index", nullable=False)
    op.drop_column("sessions", "copies")
    op.drop_column("sessions", "tab_leaves")
    op.drop_column("sessions", "question_seconds")
    op.add_column("sessions", sa.Column("deadline", sa.DateTime(timezone=True), nullable=True))
