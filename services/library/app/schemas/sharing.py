from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class ShareIn(BaseModel):
    email: EmailStr


class ShareOut(BaseModel):
    email: str
    accepted: bool
    created_at: datetime


class ShareInviteOut(BaseModel):
    """What the invited person sees before accepting."""

    preparation_id: UUID
    title: str
    email: str
    accepted: bool
