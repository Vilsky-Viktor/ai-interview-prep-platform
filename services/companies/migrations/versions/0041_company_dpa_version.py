"""companies dpa_version: the version of the data processing agreement in force when the
company was made, which its owner accepted with the terms

Revision ID: 0041
Revises: 0040
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0041"
down_revision = "0040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("dpa_version", sa.String(10)))


def downgrade() -> None:
    op.drop_column("companies", "dpa_version")
