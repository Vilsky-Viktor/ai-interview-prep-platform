"""invite name: the candidate's name from their sign-in, filled when they start; None until then
or when their sign-in has none

Revision ID: 0035
Revises: 0034
Create Date: 2026-10-09
"""

import sqlalchemy as sa
from alembic import op

revision = "0035"
down_revision = "0034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("candidate_invites", sa.Column("name", sa.String(200)))


def downgrade() -> None:
    op.drop_column("candidate_invites", "name")
