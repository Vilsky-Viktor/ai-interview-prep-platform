"""one link for many candidates: a test's shareable link

Revision ID: 0015
Revises: 0014
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("interviews", sa.Column("link_token", sa.String(64), nullable=True))
    op.create_unique_constraint("uq_interviews_link_token", "interviews", ["link_token"])


def downgrade() -> None:
    op.drop_constraint("uq_interviews_link_token", "interviews", type_="unique")
    op.drop_column("interviews", "link_token")
