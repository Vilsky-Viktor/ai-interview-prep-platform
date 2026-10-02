"""certificates keep their preparation and survive when its rounds are deleted

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("certificates", sa.Column("preparation_id", sa.Uuid(), nullable=True))
    op.execute(
        "UPDATE certificates c SET preparation_id = r.preparation_id "
        "FROM rounds r WHERE r.id = c.round_id"
    )
    op.alter_column("certificates", "preparation_id", nullable=False)
    op.alter_column("certificates", "round_id", nullable=True)
    op.drop_constraint("certificates_round_id_fkey", "certificates", type_="foreignkey")
    op.create_foreign_key(
        "certificates_round_id_fkey",
        "certificates",
        "rounds",
        ["round_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("certificates_round_id_fkey", "certificates", type_="foreignkey")
    op.execute("DELETE FROM certificates WHERE round_id IS NULL")
    op.create_foreign_key(
        "certificates_round_id_fkey",
        "certificates",
        "rounds",
        ["round_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.alter_column("certificates", "round_id", nullable=False)
    op.drop_column("certificates", "preparation_id")
