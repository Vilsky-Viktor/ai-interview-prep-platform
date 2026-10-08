"""slack_posts: the notifications already posted to Slack, so a retried event posts once

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "slack_posts",
        sa.Column("event_id", sa.String(128), primary_key=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_slack_posts_posted_at", "slack_posts", ["posted_at"])


def downgrade() -> None:
    op.drop_table("slack_posts")
