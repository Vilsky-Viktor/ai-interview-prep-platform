"""the question bank: each template question's stage, and where a test's copy came from

Revision ID: 0017
Revises: 0016
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "questions",
        sa.Column("stage", sa.String(16), nullable=False, server_default="private"),
    )
    op.add_column("questions", sa.Column("source_question_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "questions_source_question_id_fkey",
        "questions",
        "questions",
        ["source_question_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_questions_source_question_id", "questions", ["source_question_id"])
    # Templates made before the bank reveal a third of each topic too, as new ones do.
    op.execute(
        """
        UPDATE questions SET stage = 'revealed'
        WHERE position % 3 = 2 AND topic_id IN (
            SELECT t.id FROM topics t JOIN sets s ON s.id = t.set_id WHERE s.kind = 'template'
        )
        """
    )


def downgrade() -> None:
    op.drop_index("ix_questions_source_question_id", table_name="questions")
    op.drop_constraint("questions_source_question_id_fkey", "questions", type_="foreignkey")
    op.drop_column("questions", "source_question_id")
    op.drop_column("questions", "stage")
