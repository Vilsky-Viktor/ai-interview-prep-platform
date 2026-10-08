from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.constants.api import MAX_NAME_LENGTH, MAX_URL_LENGTH, KeyExpiry


class KeyOut(BaseModel):
    id: UUID
    name: str
    # The key's first characters, to tell keys apart.
    shown: str
    created_at: datetime
    # None: it never expires.
    expires_at: datetime | None
    expired: bool
    last_used_at: datetime | None


class NewKeyOut(KeyOut):
    # The whole key, shown this once.
    key: str


class KeyIn(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    expiry: KeyExpiry


class WebhookOut(BaseModel):
    id: UUID
    url: str
    created_at: datetime
    # It didn't take an event for days (it was dropped), and has taken none since.
    failing: bool


class NewWebhookOut(WebhookOut):
    # The signing secret, shown this once.
    secret: str


class WebhookIn(BaseModel):
    url: str = Field(min_length=1, max_length=MAX_URL_LENGTH)


class ApiSettingsOut(BaseModel):
    keys: list[KeyOut]
    # When a new key can expire, in order.
    expiries: list[str]
    webhooks: list[WebhookOut]
