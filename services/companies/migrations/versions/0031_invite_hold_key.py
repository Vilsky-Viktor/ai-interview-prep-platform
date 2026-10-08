"""invite hold key: each invite's own key for the credits set aside for it, so a candidate
invited again after their invite was removed is charged again

Revision ID: 0031
Revises: 0030
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0031"
down_revision = "0030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("candidate_invites", sa.Column("hold_key", sa.String(200)))


def downgrade() -> None:
    op.drop_column("candidate_invites", "hold_key")
