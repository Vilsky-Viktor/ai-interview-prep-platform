"""ats: a company's connections to its applicant tracking systems, and the jobs linked to its
interviews

Revision ID: 0028
Revises: 0027
Create Date: 2026-10-07
"""

import sqlalchemy as sa
from alembic import op

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ats_connections",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Uuid(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("account", sa.String(200), nullable=False),
        sa.Column("credentials", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("company_id", "provider"),
    )
    op.create_index("ix_ats_connections_company_id", "ats_connections", ["company_id"])
    op.create_table(
        "ats_job_links",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "connection_id",
            sa.Uuid(),
            sa.ForeignKey("ats_connections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "interview_id",
            sa.Uuid(),
            sa.ForeignKey("interviews.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("job_id", sa.String(100), nullable=False),
        sa.Column("job_name", sa.String(300), nullable=False),
        sa.Column("stage_id", sa.String(100), nullable=False),
        sa.Column("stage_name", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("connection_id", "job_id"),
    )
    op.create_index("ix_ats_job_links_connection_id", "ats_job_links", ["connection_id"])
    op.create_index("ix_ats_job_links_interview_id", "ats_job_links", ["interview_id"])


def downgrade() -> None:
    op.drop_table("ats_job_links")
    op.drop_table("ats_connections")
