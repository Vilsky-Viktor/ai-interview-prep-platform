import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditEvent(Base):
    """A human decision in a company: who made it, what, on what (an interview or a candidate's
    invite), when, and through what (via). Deleted with the company."""

    __tablename__ = "audit_events"
    __table_args__ = (Index("ix_audit_events_company_id_created_at", "company_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(64))
    target_id: Mapped[uuid.UUID | None]
    # What it was recorded through when not a person in the app: "assistant" (VIA_ASSISTANT)
    # when the in-app assistant read for the user, "mcp" (VIA_MCP) when an AI app they connected
    # did. None otherwise.
    via: Mapped[str | None] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
