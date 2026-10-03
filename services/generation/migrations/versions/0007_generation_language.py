"""the language a generation writes its content in

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "generations",
        sa.Column("language", sa.String(8), nullable=False, server_default="en"),
    )


def downgrade() -> None:
    op.drop_column("generations", "language")
