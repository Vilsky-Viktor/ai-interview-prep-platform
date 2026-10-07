"""ats candidates: candidates an ATS sends, the ATS notification of each linked job, and the
member results are written back as

Revision ID: 0029
Revises: 0028
Create Date: 2026-10-07
"""

import sqlalchemy as sa
from alembic import op

revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ats_connections", sa.Column("member_id", sa.String(100)))
    op.add_column("ats_job_links", sa.Column("subscription_id", sa.String(100)))
    op.create_table(
        "ats_candidates",
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
        sa.Column("link_id", sa.Uuid(), sa.ForeignKey("ats_job_links.id", ondelete="SET NULL")),
        sa.Column("candidate_id", sa.String(100), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True)),
        sa.Column("reason", sa.String(16)),
        sa.Column(
            "invite_id", sa.Uuid(), sa.ForeignKey("candidate_invites.id", ondelete="SET NULL")
        ),
        sa.Column("reported_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("connection_id", "candidate_id", "interview_id"),
    )
    op.create_index("ix_ats_candidates_connection_id", "ats_candidates", ["connection_id"])
    op.create_index("ix_ats_candidates_interview_id", "ats_candidates", ["interview_id"])
    op.create_index("ix_ats_candidates_invite_id", "ats_candidates", ["invite_id"])


def downgrade() -> None:
    op.drop_table("ats_candidates")
    op.drop_column("ats_job_links", "subscription_id")
    op.drop_column("ats_connections", "member_id")
