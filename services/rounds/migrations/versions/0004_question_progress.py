"""latest score per user, question and mode

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-30
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "question_progress",
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("mode", sa.String(32), nullable=False),
        sa.Column("preparation_id", sa.Uuid(), nullable=False),
        sa.Column("topic_id", sa.Uuid(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "question_id", "mode"),
    )
    op.create_index(
        "ix_question_progress_user_preparation",
        "question_progress",
        ["user_id", "preparation_id"],
    )
    # Backfill from every finished round, the same way the app rebuilds it.
    op.execute(
        """
        INSERT INTO question_progress
            (user_id, question_id, mode, preparation_id, topic_id, question_text, score, answered_at)
        SELECT DISTINCT ON (rounds.user_id, answers.question_id, rounds.mode)
            rounds.user_id, answers.question_id, rounds.mode, rounds.preparation_id,
            rounds.topic_id, asked->>'text', answers.score, rounds.finished_at
        FROM rounds
        JOIN answers ON answers.round_id = rounds.id
        CROSS JOIN LATERAL jsonb_array_elements(rounds.questions) AS asked
        WHERE rounds.status = 'finished'
          AND asked->>'id' = answers.question_id::text
        ORDER BY rounds.user_id, answers.question_id, rounds.mode, rounds.started_at DESC
        """
    )


def downgrade() -> None:
    op.drop_table("question_progress")
