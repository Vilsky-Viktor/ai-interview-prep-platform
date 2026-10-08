"""news posts, and their translations into the other languages

Revision ID: 0025
Revises: 0024
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "news",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("published_on", sa.Date(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_news_published_on_created_at", "news", ["published_on", "created_at"])
    op.create_table(
        "news_translations",
        sa.Column(
            "news_id",
            sa.Uuid(),
            sa.ForeignKey("news.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("language", sa.String(8), primary_key=True),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("news_translations")
    op.drop_table("news")
