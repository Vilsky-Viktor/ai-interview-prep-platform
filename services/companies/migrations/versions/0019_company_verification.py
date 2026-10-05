"""verified companies: the website's domain, verified by an admin's work email on it

Revision ID: 0019
Revises: 0018
Create Date: 2026-10-05
"""

import sqlalchemy as sa
from alembic import op

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("website_domain", sa.String(253), nullable=True))
    op.add_column("companies", sa.Column("verified_domain", sa.String(253), nullable=True))


def downgrade() -> None:
    op.drop_column("companies", "verified_domain")
    op.drop_column("companies", "website_domain")
