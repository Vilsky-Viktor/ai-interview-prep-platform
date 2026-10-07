"""ats: companies' connections to their applicant tracking systems, the jobs linked to their
interviews, the candidates an ATS sends, and an outbox for the events this service publishes.
Companies, interviews and invites live in the companies service: their ids are plain columns.

Revision ID: 0001
Revises:
Create Date: 2026-10-07
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ats_connections",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("account", sa.String(200), nullable=False),
        sa.Column("credentials", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("member_id", sa.String(100)),
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
        sa.Column("interview_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.String(100), nullable=False),
        sa.Column("job_name", sa.String(300), nullable=False),
        sa.Column("stage_id", sa.String(100), nullable=False),
        sa.Column("stage_name", sa.String(200), nullable=False),
        sa.Column("subscription_id", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("connection_id", "job_id"),
    )
    op.create_index("ix_ats_job_links_connection_id", "ats_job_links", ["connection_id"])
    op.create_index("ix_ats_job_links_interview_id", "ats_job_links", ["interview_id"])
    op.create_table(
        "ats_candidates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "connection_id",
            sa.Uuid(),
            sa.ForeignKey("ats_connections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("interview_id", sa.Uuid(), nullable=False),
        sa.Column("link_id", sa.Uuid(), sa.ForeignKey("ats_job_links.id", ondelete="SET NULL")),
        sa.Column("candidate_id", sa.String(100), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True)),
        sa.Column("reason", sa.String(16)),
        sa.Column("invite_id", sa.Uuid()),
        sa.Column("reported_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("connection_id", "candidate_id", "interview_id"),
    )
    op.create_index("ix_ats_candidates_connection_id", "ats_candidates", ["connection_id"])
    op.create_index("ix_ats_candidates_interview_id", "ats_candidates", ["interview_id"])
    op.create_index("ix_ats_candidates_invite_id", "ats_candidates", ["invite_id"])
    op.create_table(
        "outbox",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("data", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_outbox_published_at", "outbox", ["published_at"])


def downgrade() -> None:
    op.drop_table("outbox")
    op.drop_table("ats_candidates")
    op.drop_table("ats_job_links")
    op.drop_table("ats_connections")
