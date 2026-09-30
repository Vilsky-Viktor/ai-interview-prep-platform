"""candidate sessions

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.String(128), nullable=False, index=True),
        sa.Column("topic_id", sa.Uuid(), nullable=False, index=True),
        sa.Column("interview_set_id", sa.Uuid(), nullable=False),
        sa.Column("candidate_invite_id", sa.Uuid(), nullable=False, index=True),
        sa.Column("topic_title", sa.Text(), nullable=False),
        sa.Column("mode", sa.String(32), nullable=False),
        sa.Column("share_results", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("questions", postgresql.JSONB(), nullable=False),
        sa.Column("final_score", sa.Integer()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )
    op.alter_column("answers", "round_id", existing_type=sa.Uuid(), nullable=True)
    op.add_column(
        "answers",
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("sessions.id", ondelete="CASCADE")),
    )
    op.create_unique_constraint("uq_answers_session_question", "answers", ["session_id", "question_id"])


def downgrade() -> None:
    op.drop_constraint("uq_answers_session_question", "answers", type_="unique")
    op.drop_column("answers", "session_id")
    op.alter_column("answers", "round_id", existing_type=sa.Uuid(), nullable=False)
    op.drop_table("sessions")
