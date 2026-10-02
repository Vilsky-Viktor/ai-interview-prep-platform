"""interview title stored in companies

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Filled from generation.completed events, and once from library for older interviews.
    op.add_column("interviews", sa.Column("title", sa.Text()))


def downgrade() -> None:
    op.drop_column("interviews", "title")
