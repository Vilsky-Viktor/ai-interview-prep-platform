"""ats_connections created_by_name: who connected it, by name (or email), shown where the ATS
names no account

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-10
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ats_connections", sa.Column("created_by_name", sa.String(320)))


def downgrade() -> None:
    op.drop_column("ats_connections", "created_by_name")
