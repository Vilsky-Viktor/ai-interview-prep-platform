import uuid
from datetime import datetime

from sqlalchemy import Computed, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.search import TOPIC_SEARCH_EXPRESSION
from app.constants.sets import Visibility
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
    requirements: Mapped[list] = mapped_column(JSONB)
    visibility: Mapped[str] = mapped_column(String(32), default=Visibility.PRIVATE)
    # Stored so lists don't count per row; storage/stats.py keeps them up to date.
    topic_count: Mapped[int] = mapped_column(default=0)
    rating_sum: Mapped[int] = mapped_column(default=0)
    rating_count: Mapped[int] = mapped_column(default=0)
    join_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

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
    search: Mapped[str] = mapped_column(
        TSVECTOR, Computed(TOPIC_SEARCH_EXPRESSION, persisted=True), deferred=True
    )

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
