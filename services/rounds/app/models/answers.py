import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (UniqueConstraint("session_id", "question_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"))
    question_id: Mapped[uuid.UUID]
    # None when a timed question ran out before the candidate answered.
    option_index: Mapped[int | None]
    correct: Mapped[bool]
    # CORRECT_SCORE or 0, so averages read as percent correct.
    score: Mapped[int]
    # Interview answers only: seconds from the question being shown to it being answered.
    seconds: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
