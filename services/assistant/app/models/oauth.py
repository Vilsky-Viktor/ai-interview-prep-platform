import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def now() -> datetime:
    return datetime.now(UTC)


class OAuthClient(Base):
    """An AI app that registered itself (OAuth dynamic client registration), as it described
    itself: its name and the addresses it returns to. Deleted once it has had no connection for
    IDLE_CLIENT_DAYS."""

    __tablename__ = "oauth_clients"

    client_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    # The MCP SDK's OAuthClientInformationFull, as JSON.
    info: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class McpGrant(Base):
    """One connection: a user allowed an app to use prepza as them. Its tokens are kept as their
    hashes only; deleting the row disconnects the app."""

    __tablename__ = "mcp_grants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    client_id: Mapped[str] = mapped_column(
        ForeignKey("oauth_clients.client_id", ondelete="CASCADE"), index=True
    )
    # What the user saw when they allowed it: the app's name and the site it returns to.
    client_name: Mapped[str] = mapped_column(String(80))
    redirect_host: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    access_hash: Mapped[str] = mapped_column(String(64), unique=True)
    access_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    refresh_hash: Mapped[str] = mapped_column(String(64), unique=True)
    # Refreshing moves it on: a connection in use doesn't expire.
    refresh_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
