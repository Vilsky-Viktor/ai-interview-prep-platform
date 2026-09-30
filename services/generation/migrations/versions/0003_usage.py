"""token usage per generation

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-30
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("generations", sa.Column("usage", postgresql.JSONB()))


def downgrade() -> None:
    op.drop_column("generations", "usage")
