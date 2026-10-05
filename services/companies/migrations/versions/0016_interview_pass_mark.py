"""results view: the grade a candidate needs to pass a test

Revision ID: 0016
Revises: 0015
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interviews",
        sa.Column("pass_mark", sa.Integer(), nullable=False, server_default="70"),
    )


def downgrade() -> None:
    op.drop_column("interviews", "pass_mark")
