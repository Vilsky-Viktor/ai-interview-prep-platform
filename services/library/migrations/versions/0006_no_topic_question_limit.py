"""preparation rounds always ask every question of a topic

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("topics", "question_limit")


def downgrade() -> None:
    op.add_column("topics", sa.Column("question_limit", sa.Integer, nullable=True))
