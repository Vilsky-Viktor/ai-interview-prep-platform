"""no learners: prep kits, joins, shares, kit ratings and public search go

Revision ID: 0016
Revises: 0015
Create Date: 2026-10-05
"""

from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Their topics, questions and the questions' feedback go with them (ON DELETE CASCADE).
    op.execute("DELETE FROM sets WHERE kind <> 'interview'")
    op.drop_table("share_invites")
    op.drop_table("joined_preparations")
    op.drop_table("preparation_ratings")
    op.drop_index("ix_sets_title_trgm", table_name="sets")
    op.drop_index("ix_topics_search", table_name="topics")
    op.drop_column("topics", "search")

    for column in ("visibility", "rating_sum", "rating_count", "join_count"):
        op.drop_column("sets", column)


def downgrade() -> None:
    raise NotImplementedError("The learner data was deleted; it can't be brought back.")
