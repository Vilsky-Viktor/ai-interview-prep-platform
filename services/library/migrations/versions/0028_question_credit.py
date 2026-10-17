"""Right answers become credit: a multi-answer ("select all that apply") answer earns part of a
point (2 of 3 right options ticked, no wrong one: 0.67), so the right-answer counts of a
question's statistics and revisions hold fractions.

Revision ID: 0028
Revises: 0027
Create Date: 2026-10-17
"""

import sqlalchemy as sa
from alembic import op

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None

COLUMNS = (
    ("question_stats", "correct"),
    ("question_stats", "strong_correct"),
    ("question_stats", "weak_correct"),
    ("question_revisions", "correct"),
)


def upgrade() -> None:
    for table, column in COLUMNS:
        op.alter_column(table, column, type_=sa.Float(), existing_type=sa.Integer())


def downgrade() -> None:
    for table, column in COLUMNS:
        op.alter_column(
            table,
            column,
            type_=sa.Integer(),
            existing_type=sa.Float(),
            postgresql_using=f"round({column})::integer",
        )
