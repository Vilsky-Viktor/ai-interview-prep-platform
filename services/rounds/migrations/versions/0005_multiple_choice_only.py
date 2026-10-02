"""multiple choice only

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Open answer rounds and sessions can't become multiple choice. Deleting them also deletes
    # their answers, follow-up chats and certificates (foreign keys cascade).
    op.execute("DELETE FROM rounds WHERE mode = 'open'")
    op.execute("DELETE FROM sessions WHERE mode = 'open'")
    op.execute("DELETE FROM question_progress WHERE mode = 'open'")

    op.drop_constraint("question_progress_pkey", "question_progress", type_="primary")
    op.drop_column("question_progress", "mode")
    op.create_primary_key("question_progress_pkey", "question_progress", ["user_id", "question_id"])

    op.drop_column("rounds", "mode")
    op.drop_column("sessions", "mode")
    op.drop_column("answers", "text")
    op.drop_column("answers", "feedback")
    op.alter_column("answers", "option_index", nullable=False)
    op.alter_column("answers", "correct", nullable=False)


def downgrade() -> None:
    """Restores the columns; the deleted open answer data doesn't come back."""
    op.alter_column("answers", "correct", nullable=True)
    op.alter_column("answers", "option_index", nullable=True)
    op.add_column("answers", sa.Column("feedback", sa.Text()))
    op.add_column("answers", sa.Column("text", sa.Text()))
    op.add_column(
        "sessions", sa.Column("mode", sa.String(32), nullable=False, server_default="choice")
    )
    op.add_column(
        "rounds", sa.Column("mode", sa.String(32), nullable=False, server_default="choice")
    )
    op.drop_constraint("question_progress_pkey", "question_progress", type_="primary")
    op.add_column(
        "question_progress",
        sa.Column("mode", sa.String(32), nullable=False, server_default="choice"),
    )
    op.create_primary_key(
        "question_progress_pkey", "question_progress", ["user_id", "question_id", "mode"]
    )
