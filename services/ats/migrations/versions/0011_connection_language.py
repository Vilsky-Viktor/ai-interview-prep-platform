"""ats_connections language: the interface language of the member who connected it, which
results written back to the ATS are in

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-15
"""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ats_connections", sa.Column("language", sa.String(8)))


def downgrade() -> None:
    op.drop_column("ats_connections", "language")
