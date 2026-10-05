"""no learners: practice rounds, the tutor chat, certificates and progress go

Revision ID: 0016
Revises: 0015
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("certificates")
    op.drop_table("question_progress")
    # A practice round's answers; a candidate's always have a session.
    op.execute("DELETE FROM answers WHERE session_id IS NULL")
    op.drop_column("answers", "round_id")
    op.drop_table("rounds")
    op.alter_column("answers", "session_id", existing_type=sa.Uuid(), nullable=False)


def downgrade() -> None:
    raise NotImplementedError("The learner data was deleted; it can't be brought back.")
