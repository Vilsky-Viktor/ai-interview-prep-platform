import uuid
from datetime import datetime

from prepza_common.constants import DEFAULT_LANGUAGE
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.sets import Stage
from app.models.base import Base


class QuestionSet(Base):
    """A generated preparation or company interview: topics with their questions."""

    __tablename__ = "sets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # Null for sets saved before generations were tracked.
    generation_id: Mapped[uuid.UUID | None] = mapped_column(unique=True)
    kind: Mapped[str] = mapped_column(String(32))
    owner_type: Mapped[str] = mapped_column(String(32))
    owner_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(200))
    source_text: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(32))
    # The language its content was generated in; reuse only mixes sets of one language.
    language: Mapped[str] = mapped_column(String(8), default=DEFAULT_LANGUAGE)
    requirements: Mapped[list] = mapped_column(JSONB)
    # Stored so lists don't count per row; storage/stats.py keeps them up to date.
    topic_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    topics: Mapped[list["Topic"]] = relationship(
        order_by="Topic.position", cascade="all, delete-orphan"
    )


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    set_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sets.id", ondelete="CASCADE"), index=True)
    position: Mapped[int]
    title: Mapped[str] = mapped_column(Text)
    subtopics: Mapped[list] = mapped_column(JSONB)

    questions: Mapped[list["Question"]] = relationship(
        order_by="Question.position", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int]
    text: Mapped[str] = mapped_column(Text)
    options: Mapped[list] = mapped_column(JSONB)
    # A template question's stage in the bank (constants/sets.py Stage); private elsewhere.
    stage: Mapped[str] = mapped_column(String(16), default=Stage.PRIVATE)
    # A company test's copy of a bank question: its answers count for the original too.
    source_question_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("questions.id", ondelete="SET NULL"), index=True
    )
