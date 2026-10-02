"""questions are multiple choice only and have no written reference answer

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("questions", "reference_answer")


def downgrade() -> None:
    op.add_column(
        "questions",
        sa.Column("reference_answer", sa.Text(), nullable=False, server_default=""),
    )
