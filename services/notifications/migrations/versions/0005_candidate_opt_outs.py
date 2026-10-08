"""candidate_opt_outs: candidates who asked a company's emails, or an invite's reminders, to stop

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "candidate_opt_outs",
        sa.Column("id", sa.Integer, primary_key=True),
        # The address's SHA-256, never the address.
        sa.Column("address", sa.String(64), nullable=False),
        sa.Column("company_id", sa.String(128), nullable=False),
        sa.Column("invite_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "uq_candidate_opt_outs",
        "candidate_opt_outs",
        ["address", "company_id", "invite_id"],
        unique=True,
        postgresql_nulls_not_distinct=True,
    )
    op.create_index("ix_candidate_opt_outs_company_id", "candidate_opt_outs", ["company_id"])


def downgrade() -> None:
    op.drop_table("candidate_opt_outs")
