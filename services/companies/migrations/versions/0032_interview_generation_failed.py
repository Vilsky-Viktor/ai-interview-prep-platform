"""interview generation failed: generation's generation.failed event marks the interview, so
its lists show the failure without asking generation for each row

Revision ID: 0032
Revises: 0031
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0032"
down_revision = "0031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interviews",
        sa.Column("generation_failed", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("interviews", "generation_failed")
