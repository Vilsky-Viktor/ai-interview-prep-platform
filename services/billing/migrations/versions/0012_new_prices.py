"""auto_top_ups on the new prices: each saved choice moves to the top-up that replaced its own
($30 to $50, $150 to $200, $250 to $600), and its threshold keeps its number of candidates (a
candidate is 500 credits, was 300)

Revision ID: 0012
Revises: 0011
Create Date: 2026-10-14
"""

from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None

PRODUCTS = {"topup_30": "topup_50", "topup_150": "topup_200", "topup_250": "topup_600"}


def upgrade() -> None:
    for old, new in PRODUCTS.items():
        op.execute(f"UPDATE auto_top_ups SET product = '{new}' WHERE product = '{old}'")

    op.execute("UPDATE auto_top_ups SET threshold = threshold / 300 * 500")


def downgrade() -> None:
    for old, new in PRODUCTS.items():
        op.execute(f"UPDATE auto_top_ups SET product = '{old}' WHERE product = '{new}'")

    op.execute("UPDATE auto_top_ups SET threshold = threshold / 500 * 300")
