"""ai_usage and limit_hits: every AI call and limit refusal, for the admin zone's AI costs tab;
limit_settings and limit_changes: the limits superadmins edit in Controls, and their history

Revision ID: 0015
Revises: 0014
Create Date: 2026-10-16
"""

import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_usage",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("event_id", sa.String(128), nullable=False, unique=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("action", sa.String(48), nullable=False),
        sa.Column("service", sa.String(32), nullable=False),
        sa.Column("model", sa.String(64), nullable=False),
        sa.Column("input_tokens", sa.BigInteger(), nullable=False),
        sa.Column("cached_input_tokens", sa.BigInteger(), nullable=False),
        sa.Column("output_tokens", sa.BigInteger(), nullable=False),
        sa.Column("audio_seconds", sa.Float(), nullable=False),
        sa.Column("cost_usd", sa.Float(), nullable=False),
        sa.Column("company_id", sa.String(128), nullable=True),
        sa.Column("user_id", sa.String(128), nullable=True),
        sa.Column("subject_id", sa.String(128), nullable=True),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("category", sa.String(16), nullable=False),
    )
    op.create_index("ix_ai_usage_occurred_at", "ai_usage", ["occurred_at"])
    op.create_index("ix_ai_usage_company_id", "ai_usage", ["company_id"])
    op.create_index("ix_ai_usage_user_id", "ai_usage", ["user_id"])
    op.create_table(
        "limit_hits",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("event_id", sa.String(128), nullable=False, unique=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("limit", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(48), nullable=False),
        sa.Column("scope", sa.String(16), nullable=False),
        sa.Column("company_id", sa.String(128), nullable=True),
        sa.Column("user_id", sa.String(128), nullable=True),
        sa.Column("what", sa.String(64), nullable=True),
    )
    op.create_index("ix_limit_hits_occurred_at", "limit_hits", ["occurred_at"])
    op.create_index("ix_limit_hits_company_id", "limit_hits", ["company_id"])
    op.create_index("ix_limit_hits_user_id", "limit_hits", ["user_id"])
    op.create_table(
        "limit_settings",
        sa.Column("name", sa.String(64), primary_key=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "limit_changes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("old_value", sa.Float(), nullable=True),
        sa.Column("new_value", sa.Float(), nullable=True),
        sa.Column("changed_by", sa.String(128), nullable=False),
        sa.Column("changed_by_email", sa.String(320), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_limit_changes_changed_at", "limit_changes", ["changed_at"])


def downgrade() -> None:
    op.drop_table("limit_changes")
    op.drop_table("limit_settings")
    op.drop_table("limit_hits")
    op.drop_table("ai_usage")
