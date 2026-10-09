"""ats_candidates name: the candidate's name as the ATS sent it, for their invite; None when it
sent none

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-09
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ats_candidates", sa.Column("name", sa.String(200)))


def downgrade() -> None:
    op.drop_column("ats_candidates", "name")
