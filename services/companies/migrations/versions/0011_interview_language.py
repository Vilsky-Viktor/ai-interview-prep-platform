"""the language each interview is generated in, for its invite emails

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-03
"""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Interviews made before languages existed are English, as their sets in library are.
    op.add_column(
        "interviews",
        sa.Column("language", sa.String(8), nullable=False, server_default="en"),
    )


def downgrade() -> None:
    op.drop_column("interviews", "language")
