import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class QuestionProgress(Base):
    """A user's latest score per question, counting rounds still in progress.

    Derived from rounds and answers, and rebuilt for a question whenever it is answered or a
    round with it is deleted. `question_text` is the text that was answered, so a question
    re-generated since then no longer matches the library's current text.
    """

    __tablename__ = "question_progress"
    __table_args__ = (Index("ix_question_progress_user_preparation", "user_id", "preparation_id"),)

    user_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    question_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    preparation_id: Mapped[uuid.UUID]
    topic_id: Mapped[uuid.UUID]
    question_text: Mapped[str] = mapped_column(Text)
    score: Mapped[int]
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
