"""companies ai_apps_off_at: since when members may not use the company's data from AI apps
they connected (Claude, ChatGPT, ...); its owners and admins decide

Revision ID: 0040
Revises: 0039
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0040"
down_revision = "0039"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("ai_apps_off_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("companies", "ai_apps_off_at")
