import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Wallet(Base):
    """One credit balance. `reserved` is set aside for something that hasn't finished."""

    __tablename__ = "wallets"

    owner_type: Mapped[str] = mapped_column(String(16), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    balance: Mapped[int] = mapped_column(default=0)
    reserved: Mapped[int] = mapped_column(default=0)


class Gift(Base):
    """A welcome gift already given, by a one-way hash of the email. Kept when the account or
    company is deleted, so signing up again doesn't give the gift again."""

    __tablename__ = "gifts"

    key: Mapped[str] = mapped_column(String(160), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class Hold(Base):
    """Credits set aside for one piece of work, charged or given back later."""

    __tablename__ = "holds"

    key: Mapped[str] = mapped_column(String(160), primary_key=True)
    owner_type: Mapped[str] = mapped_column(String(16))
    owner_id: Mapped[str] = mapped_column(String(128))
    amount: Mapped[int]
    reason: Mapped[str] = mapped_column(String(64))
    # open, charged or released.
    status: Mapped[str] = mapped_column(String(16))


class Entry(Base):
    """One movement of credits: a gift or top-up (positive), or a charge (negative). The key
    makes a repeated call count once. Together they're the wallet's history."""

    __tablename__ = "entries"
    __table_args__ = (UniqueConstraint("key", name="uq_entries_key"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(160))
    owner_type: Mapped[str] = mapped_column(String(16))
    owner_id: Mapped[str] = mapped_column(String(128), index=True)
    amount: Mapped[int]
    reason: Mapped[str] = mapped_column(String(64))
    # What it was for, for example a certificate's topic; never personal data.
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


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
