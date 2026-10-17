"""generations.question_count, and one question addition at a time for a template: adding
questions to an existing template's topics, a top-up or a superadmin's addition

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("generations", sa.Column("question_count", sa.Integer(), nullable=True))
    op.create_index(
        "ix_generations_one_addition_per_template",
        "generations",
        ["preparation_id"],
        unique=True,
        postgresql_where=sa.text("kind = 'template_questions' AND status IN ('queued', 'running')"),
    )


def downgrade() -> None:
    op.drop_index("ix_generations_one_addition_per_template", table_name="generations")
    op.drop_column("generations", "question_count")
