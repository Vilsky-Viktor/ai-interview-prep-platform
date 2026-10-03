"""the language a set's content was generated in

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
    op.add_column(
        "sets",
        sa.Column("language", sa.String(8), nullable=False, server_default="en"),
    )


def downgrade() -> None:
    op.drop_column("sets", "language")
