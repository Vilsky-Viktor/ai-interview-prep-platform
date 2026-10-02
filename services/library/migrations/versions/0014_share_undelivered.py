"""when a share invite's email bounced or was marked as spam

Revision ID: 0014
Revises: 0013
Create Date: 2026-10-02
"""

import sqlalchemy as sa
from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "share_invites",
        sa.Column("undelivered_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("share_invites", "undelivered_at")
