import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def now() -> datetime:
    return datetime.now(UTC)


class Conversation(Base):
    """A user's chat with the assistant, about one company (or none)."""

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    # The first 80 characters of the first message.
    title: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    # The last message's time: conversations idle longer than the retention are deleted.
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)


class Message(Base):
    """One message: the user's (typed or spoken) or the assistant's answer with its blocks."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    # "user" or "assistant".
    role: Mapped[str] = mapped_column(String(16))
    # "text" or "voice" (transcribed; the audio itself is never kept).
    source: Mapped[str] = mapped_column(String(8), default="text")
    content: Mapped[str] = mapped_column(Text)
    # What the panel shows under an answer: candidate rows, links and the like.
    blocks: Mapped[list] = mapped_column(JSONB, default=list)
    # "complete", "cancelled" (stopped, with its partial text) or "failed".
    status: Mapped[str] = mapped_column(String(16), default="complete")
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ToolCall(Base):
    """A tool an answer used: a GET to another service, with the trimmed data the model read."""

    __tablename__ = "tool_calls"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), index=True
    )
    tool: Mapped[str] = mapped_column(String(64))
    arguments: Mapped[dict] = mapped_column(JSONB)
    # The service's answer; None when it didn't answer.
    status_code: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int] = mapped_column(Integer)
    result: Mapped[dict | None] = mapped_column(JSONB)
    # "done" or "failed".
    state: Mapped[str] = mapped_column(String(32), default="done")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
