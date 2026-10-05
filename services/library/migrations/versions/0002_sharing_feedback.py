"""topic search, share invites, joined preparations, ratings, reports

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def set_fk() -> sa.Column:
    return sa.Column(
        "set_id", sa.Uuid(), sa.ForeignKey("sets.id", ondelete="CASCADE"), nullable=False
    )


def question_fk(**kwargs) -> sa.Column:
    return sa.Column(
        "question_id",
        sa.Uuid(),
        sa.ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        **kwargs,
    )


def upgrade() -> None:
    op.add_column(
        "topics",
        sa.Column(
            "search",
            postgresql.TSVECTOR(),
            sa.Computed("to_tsvector('english', title || ' ' || subtopics::text)", persisted=True),
        ),
    )
    op.create_index("ix_topics_search", "topics", ["search"], postgresql_using="gin")
    op.create_table(
        "share_invites",
        sa.Column("id", sa.Uuid(), primary_key=True),
        set_fk(),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("token", sa.String(64), nullable=False, unique=True),
        sa.Column("invited_by", sa.String(128), nullable=False),
        sa.Column("accepted_by", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("set_id", "email"),
    )
    op.create_table(
        "joined_preparations",
        set_fk(),
        sa.Column("user_id", sa.String(128), nullable=False, index=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("set_id", "user_id"),
    )
    op.create_table(
        "preparation_ratings",
        set_fk(),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("value", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("set_id", "user_id"),
    )
    op.create_table(
        "question_ratings",
        question_fk(),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("value", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("question_id", "user_id"),
    )
    op.create_table(
        "question_reports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        question_fk(index=True),
        sa.Column("user_id", sa.String(128), nullable=False),
        sa.Column("reason", sa.String(32), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("question_reports")
    op.drop_table("question_ratings")
    op.drop_table("preparation_ratings")
    op.drop_table("joined_preparations")
    op.drop_table("share_invites")
    op.drop_index("ix_topics_search", "topics")
    op.drop_column("topics", "search")
