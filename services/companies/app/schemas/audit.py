from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditEventOut(BaseModel):
    user_id: str
    action: str
    target_id: UUID | None
    # "assistant" when the in-app assistant read for the user, "mcp" when an AI app they
    # connected did; None for the app itself.
    via: str | None = None
    created_at: datetime
