"""audit events: the human decisions in a company, as evidence of oversight

Revision ID: 0022
Revises: 0021
Create Date: 2026-10-06
"""

import sqlalchemy as sa
from alembic import op

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Uuid(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_audit_events_company_id_created_at", "audit_events", ["company_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_audit_events_company_id_created_at", table_name="audit_events")
    op.drop_table("audit_events")
