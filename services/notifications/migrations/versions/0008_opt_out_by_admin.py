"""candidate_opt_outs.by_admin: a stop a superadmin made, which only a superadmin lifts; the
candidate's own, from an email's link, stays

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "candidate_opt_outs",
        sa.Column("by_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("candidate_opt_outs", "by_admin")
