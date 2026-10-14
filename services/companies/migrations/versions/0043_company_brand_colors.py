"""companies brand_colors, brand_font and brand_radius, and candidate_invites theme: a company's
own colors (by theme), font and corner rounding on its candidates' pages, and the theme an
invite's pages show (as the API asked)

Revision ID: 0043
Revises: 0042
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0043"
down_revision = "0042"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("brand_colors", JSONB()))
    op.add_column("companies", sa.Column("brand_font", sa.String(32)))
    op.add_column("companies", sa.Column("brand_radius", sa.SmallInteger()))
    op.add_column("companies", sa.Column("brand_button_radius", sa.SmallInteger()))
    op.add_column("candidate_invites", sa.Column("theme", sa.String(8)))


def downgrade() -> None:
    op.drop_column("candidate_invites", "theme")
    op.drop_column("companies", "brand_button_radius")
    op.drop_column("companies", "brand_radius")
    op.drop_column("companies", "brand_font")
    op.drop_column("companies", "brand_colors")
