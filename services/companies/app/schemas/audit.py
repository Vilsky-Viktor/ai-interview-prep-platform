from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditEventOut(BaseModel):
    user_id: str
    action: str
    target_id: UUID | None
    created_at: datetime
