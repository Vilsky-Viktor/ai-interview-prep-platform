from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CertificateOut(BaseModel):
    """Public: anyone with the link can see it."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_name: str
    topic_title: str
    score: int
    issued_at: datetime
    preparation_id: UUID
