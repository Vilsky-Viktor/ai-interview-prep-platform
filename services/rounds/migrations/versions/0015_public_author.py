"""which rounds are on someone else's public kit, for paid certificates and the daily limit

Revision ID: 0015
Revises: 0014
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("rounds", sa.Column("public_author_id", sa.String(128), nullable=True))


def downgrade() -> None:
    op.drop_column("rounds", "public_author_id")
