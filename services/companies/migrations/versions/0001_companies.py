"""companies, members, interviews, candidate invites

Revision ID: 0001
Revises:
Create Date: 2026-09-29
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "members",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("company_id", sa.Uuid(), sa.ForeignKey("companies.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.String(128), index=True),
        sa.Column("invited_email", sa.String(320), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("company_id", "invited_email"),
    )
    op.create_table(
        "interviews",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Uuid(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("set_id", sa.Uuid()),
        sa.Column("generation_id", sa.Uuid(), nullable=False),
        sa.Column("mode", sa.String(32), nullable=False),
        sa.Column("share_results", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "candidate_invites",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "interview_id",
            sa.Uuid(),
            sa.ForeignKey("interviews.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("token", sa.String(64), nullable=False, unique=True),
        sa.Column("user_id", sa.String(128)),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("interview_id", "email"),
    )


def downgrade() -> None:
    op.drop_table("candidate_invites")
    op.drop_table("interviews")
    op.drop_table("members")
    op.drop_table("companies")
