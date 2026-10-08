"""sets remember when they last changed, for the sitemap's "last modified"

Revision ID: 0022
Revises: 0021
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sets",
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    # Unchanged since they were made, as far as anyone knows.
    op.execute("UPDATE sets SET updated_at = created_at")


def downgrade() -> None:
    op.drop_column("sets", "updated_at")
