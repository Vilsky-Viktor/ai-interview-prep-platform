"""sent_emails: the activity digests and reminders sent to users, so none is sent twice

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sent_emails",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("key", sa.String(160), nullable=False),
        sa.Column("sent_on", sa.Date, nullable=False),
        sa.UniqueConstraint("user_id", "kind", "key"),
    )
    op.create_index("ix_sent_emails_sent_on", "sent_emails", ["sent_on"])


def downgrade() -> None:
    op.drop_table("sent_emails")
