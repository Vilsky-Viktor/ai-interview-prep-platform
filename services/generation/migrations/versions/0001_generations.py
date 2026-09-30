"""generations

Revision ID: 0001
Revises:
Create Date: 2026-09-28
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "generations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_uid", sa.String(128), nullable=False, index=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("topics", postgresql.JSONB()),
        sa.Column("progress", postgresql.JSONB()),
        sa.Column("preparation_id", sa.Uuid()),
        sa.Column("error", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("generations")
