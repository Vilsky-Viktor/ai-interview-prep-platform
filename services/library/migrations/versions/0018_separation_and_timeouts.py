"""question statistics: how strong and weak candidates did, and how often time ran out

Revision ID: 0018
Revises: 0017
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None

COLUMNS = ("strong_answers", "strong_correct", "weak_answers", "weak_correct", "timeouts")


def upgrade() -> None:
    for column in COLUMNS:
        op.add_column(
            "question_stats",
            sa.Column(column, sa.Integer(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    for column in COLUMNS:
        op.drop_column("question_stats", column)
