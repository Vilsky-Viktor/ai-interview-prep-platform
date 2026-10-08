"""email preferences per user, and the log of every consent given or withdrawn

Revision ID: 0023
Revises: 0022
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def setting(name: str, default: bool) -> sa.Column:
    return sa.Column(
        name, sa.Boolean(), nullable=False, server_default=sa.true() if default else sa.false()
    )


def upgrade() -> None:
    op.create_table(
        "email_preferences",
        sa.Column("user_id", sa.String(128), primary_key=True),
        setting("candidate_finished", True),
        setting("invite_undelivered", True),
        setting("ats_not_invited", True),
        setting("interview_ready", True),
        setting("reminders", True),
        setting("updates", False),
        setting("promotions", False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "email_consents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.String(128), nullable=False, index=True),
        sa.Column("setting", sa.String(32), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False),
        sa.Column("source", sa.String(16), nullable=False),
        sa.Column("basis", sa.String(16), nullable=False),
        sa.Column("text_version", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("email_consents")
    op.drop_table("email_preferences")
