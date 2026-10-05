"""a company member trying their own test: a preview session, kept out of question statistics

Revision ID: 0017
Revises: 0016
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions", sa.Column("preview", sa.Boolean(), nullable=False, server_default="false")
    )


def downgrade() -> None:
    op.drop_column("sessions", "preview")
