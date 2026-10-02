"""progress counts answers from rounds still in progress

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-01
"""

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def rebuild(only_finished: bool) -> None:
    finished = "AND rounds.status = 'finished'" if only_finished else ""
    op.execute("DELETE FROM question_progress")
    op.execute(
        f"""
        INSERT INTO question_progress
            (user_id, question_id, preparation_id, topic_id, question_text, score, answered_at)
        SELECT DISTINCT ON (rounds.user_id, answers.question_id)
            rounds.user_id, answers.question_id, rounds.preparation_id,
            rounds.topic_id, asked->>'text', answers.score, answers.created_at
        FROM rounds
        JOIN answers ON answers.round_id = rounds.id
        CROSS JOIN LATERAL jsonb_array_elements(rounds.questions) AS asked
        WHERE asked->>'id' = answers.question_id::text {finished}
        ORDER BY rounds.user_id, answers.question_id, answers.created_at DESC
        """
    )


def upgrade() -> None:
    rebuild(only_finished=False)


def downgrade() -> None:
    rebuild(only_finished=True)
