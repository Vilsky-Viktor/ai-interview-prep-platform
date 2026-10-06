"""drop talent links: talent suggestions are removed

Revision ID: 0021
Revises: 0020
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("talent_links")


def downgrade() -> None:
    op.create_table(
        "talent_links",
        sa.Column("user_id", sa.String(128), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
    )
