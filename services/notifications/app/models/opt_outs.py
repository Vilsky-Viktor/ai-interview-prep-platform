from datetime import UTC, datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CandidateOptOut(Base):
    """A candidate who asked a company's emails to stop, from a link in one: every email from the
    company to this address, or (with `invite_id`) only that invite's reminders. The address is
    kept as its SHA-256 (helpers/unsubscribe.py address_hash), never in the clear. Kept when the
    company erases the candidate, so their wish outlives it; gone with the company."""

    __tablename__ = "candidate_opt_outs"
    __table_args__ = (
        # One row per wish: the same link used twice adds nothing.
        Index(
            "uq_candidate_opt_outs",
            "address",
            "company_id",
            "invite_id",
            unique=True,
            postgresql_nulls_not_distinct=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(64))
    company_id: Mapped[str] = mapped_column(String(128), index=True)
    invite_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
