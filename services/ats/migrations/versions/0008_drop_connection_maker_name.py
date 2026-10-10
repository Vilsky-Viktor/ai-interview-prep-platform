"""ats_connections created_by_name dropped: where the ATS names no account, the page shows the
company's name instead, so no member's name is kept

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-10
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("ats_connections", "created_by_name")


def downgrade() -> None:
    op.add_column("ats_connections", sa.Column("created_by_name", sa.String(320)))
