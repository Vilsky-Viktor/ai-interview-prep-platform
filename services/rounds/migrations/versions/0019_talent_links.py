"""talent pool: a talent's answer to being suggested to companies, with their link

Revision ID: 0019
Revises: 0018
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "talent_links",
        sa.Column("user_id", sa.String(128), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("talent_links")
