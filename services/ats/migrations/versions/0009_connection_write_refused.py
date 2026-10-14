"""ats_connections write_refused_at: when the ATS refused the results written back while the key
still read, so the company is told once

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ats_connections", sa.Column("write_refused_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("ats_connections", "write_refused_at")
