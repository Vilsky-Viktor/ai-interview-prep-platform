import uuid
from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Wallet(Base):
    """What a company or a user can still use: credits, and a learner's pass."""

    __tablename__ = "wallets"

    owner_type: Mapped[str] = mapped_column(String(16), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    candidate_credits: Mapped[int] = mapped_column(default=0)
    generation_credits: Mapped[int] = mapped_column(default=0)
    pass_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MonthlyUsage(Base):
    """Free preparations a learner has used in a month."""

    __tablename__ = "monthly_usage"

    user_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    month: Mapped[date] = mapped_column(Date, primary_key=True)
    free_generations: Mapped[int] = mapped_column(default=0)


class Purchase(Base):
    """One paid Paddle transaction line. Kept for bookkeeping; anonymised when the buyer deletes
    their account."""

    __tablename__ = "purchases"
    __table_args__ = (
        UniqueConstraint("transaction_id", "product", name="uq_purchases_transaction_product"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[str] = mapped_column(String(64), index=True)
    product: Mapped[str] = mapped_column(String(64))
    quantity: Mapped[int]
    owner_type: Mapped[str] = mapped_column(String(16))
    owner_id: Mapped[str] = mapped_column(String(128), index=True)
    # Who paid, when a company buys; the company is the owner.
    buyer_id: Mapped[str | None] = mapped_column(String(128))
    total: Mapped[str] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(String(3))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
