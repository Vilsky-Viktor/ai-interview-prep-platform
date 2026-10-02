"""quality flag per question, and whether the verifier kept it as it is

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("question_stats", sa.Column("flag", sa.String(32), nullable=True))
    op.add_column(
        "question_stats",
        sa.Column("kept", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("question_stats", "kept")
    op.drop_column("question_stats", "flag")
