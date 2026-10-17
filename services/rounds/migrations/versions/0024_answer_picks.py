"""Multi-answer ("select all that apply") questions: an answer keeps every option ticked
(`picks`), and whether its time ran out moves to its own column (`timed_out`) instead of being
read from a missing `option_index`, which a multi-answer answer leaves empty too.

Revision ID: 0024
Revises: 0023
Create Date: 2026-10-17
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "answers",
        sa.Column("timed_out", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute("UPDATE answers SET timed_out = true WHERE option_index IS NULL")
    op.add_column("answers", sa.Column("picks", postgresql.ARRAY(sa.SmallInteger()), nullable=True))


def downgrade() -> None:
    op.drop_column("answers", "picks")
    op.drop_column("answers", "timed_out")
