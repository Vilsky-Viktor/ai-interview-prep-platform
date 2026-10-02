import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.rounds import RoundStatus
from app.models.base import Base
from app.models.signals import Signal


class Session(Base):
    """One pass by a candidate through an interview topic. Single pass, no reveal."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    topic_id: Mapped[uuid.UUID] = mapped_column(index=True)
    interview_set_id: Mapped[uuid.UUID]
    candidate_invite_id: Mapped[uuid.UUID] = mapped_column(index=True)
    topic_title: Mapped[str] = mapped_column(Text)
    share_results: Mapped[bool]
    status: Mapped[str] = mapped_column(String(32), default=RoundStatus.IN_PROGRESS)
    questions: Mapped[list] = mapped_column(JSONB)
    final_score: Mapped[int | None]
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Timed interviews only: the seconds each question has before it counts as wrong.
    question_seconds: Mapped[int | None]
    # When the question now waiting for an answer was first shown; cleared by the answer.
    question_shown_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    answers: Mapped[list["Answer"]] = relationship(order_by="Answer.created_at")
    signals: Mapped[list[Signal]] = relationship(order_by=Signal.created_at)
