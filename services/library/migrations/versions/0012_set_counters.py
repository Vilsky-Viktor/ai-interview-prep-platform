"""stored counts on sets instead of counting per page, and a trigram index for title search

Revision ID: 0012
Revises: 0011
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None

COUNTERS = ("topic_count", "rating_sum", "rating_count", "join_count")


def upgrade() -> None:
    for column in COUNTERS:
        op.add_column(
            "sets", sa.Column(column, sa.Integer(), nullable=False, server_default="0")
        )

    op.execute(
        """
        UPDATE sets SET
            topic_count = (SELECT count(*) FROM topics WHERE topics.set_id = sets.id),
            rating_sum = (SELECT coalesce(sum(value), 0) FROM preparation_ratings r
                          WHERE r.set_id = sets.id),
            rating_count = (SELECT count(*) FROM preparation_ratings r WHERE r.set_id = sets.id),
            join_count = (SELECT count(*) FROM joined_preparations j WHERE j.set_id = sets.id)
        """
    )
    # Title search matches anywhere in the title (ILIKE '%q%'); trigrams let it use an index.
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE INDEX ix_sets_title_trgm ON sets USING gin (title gin_trgm_ops)")


def downgrade() -> None:
    op.execute("DROP INDEX ix_sets_title_trgm")

    for column in COUNTERS:
        op.drop_column("sets", column)
