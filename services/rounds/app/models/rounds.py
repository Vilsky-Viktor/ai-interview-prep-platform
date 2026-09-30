import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.rounds import RoundStatus
from app.models.base import Base
from app.models.certificates import Certificate


class Round(Base):
    __tablename__ = "rounds"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    topic_id: Mapped[uuid.UUID] = mapped_column(index=True)
    preparation_id: Mapped[uuid.UUID]
    topic_title: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default=RoundStatus.IN_PROGRESS)
    # Snapshot of the topic's questions in this round's shuffled order, with reference answers.
    questions: Mapped[list] = mapped_column(JSONB)
    final_score: Mapped[int | None]
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    answers: Mapped[list["Answer"]] = relationship(order_by="Answer.created_at")
    certificate: Mapped[Certificate | None] = relationship()


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("round_id", "question_id"),
        UniqueConstraint("session_id", "question_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    round_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("rounds.id", ondelete="CASCADE"))
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE")
    )
    question_id: Mapped[uuid.UUID]
    text: Mapped[str | None] = mapped_column(Text)
    option_index: Mapped[int | None]
    correct: Mapped[bool | None]
    score: Mapped[int]
    feedback: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
