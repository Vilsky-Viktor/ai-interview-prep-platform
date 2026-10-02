"""stop recording token usage per generation

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("generations", "usage")


def downgrade() -> None:
    op.add_column("generations", sa.Column("usage", postgresql.JSONB()))
