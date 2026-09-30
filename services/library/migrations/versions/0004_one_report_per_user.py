"""one report per user and question

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-30
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM question_reports AS report
        USING question_reports AS earlier
        WHERE report.question_id = earlier.question_id
          AND report.user_id = earlier.user_id
          AND (report.created_at, report.id) > (earlier.created_at, earlier.id)
        """
    )
    op.create_unique_constraint(
        "uq_question_reports_question_user", "question_reports", ["question_id", "user_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_question_reports_question_user", "question_reports", type_="unique")
