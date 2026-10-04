from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    """What the bell shows: `kind` picks the text, `data` fills it, `link` opens the page."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: str
    link: str
    data: dict
    created_at: datetime


class FeedOut(BaseModel):
    items: list[NotificationOut]
    # Newer than the user's last look at the bell.
    unread: int
