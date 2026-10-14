"""signals away_seconds: how long a page leave lasted, so a moment's leave isn't counted

Revision ID: 0023
Revises: 0022
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("away_seconds", sa.Float()))


def downgrade() -> None:
    op.drop_column("signals", "away_seconds")
