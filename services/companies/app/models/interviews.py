import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, false
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.interviews import DEFAULT_QUESTION_SECONDS
from app.models.base import Base

# For the relationship's annotation only; the class is resolved by name at runtime.
if TYPE_CHECKING:
    from app.models.invites import CandidateInvite


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    set_id: Mapped[uuid.UUID | None]
    # Copied from the generated set (and renames), so pages don't ask library for it.
    title: Mapped[str | None] = mapped_column(Text)
    generation_id: Mapped[uuid.UUID]
    share_results: Mapped[bool]
    # In a timed interview every question has question_seconds; one left unanswered is wrong.
    timed: Mapped[bool] = mapped_column(default=False, server_default=false())
    question_seconds: Mapped[int] = mapped_column(
        default=DEFAULT_QUESTION_SECONDS, server_default=str(DEFAULT_QUESTION_SECONDS)
    )
    topic_limits: Mapped[dict[str, int]] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    invites: Mapped[list["CandidateInvite"]] = relationship(cascade="all, delete-orphan")
