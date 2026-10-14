from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AccessOut(BaseModel):
    # Any member (owner, admin or viewer); an editor is an owner or admin.
    member: bool
    editor: bool


class InterviewBriefOut(BaseModel):
    id: UUID
    company_id: UUID
    title: str | None
    # It has its questions, so candidates can be invited.
    ready: bool


class AtsInviteIn(BaseModel):
    email: EmailStr
    # Whoever connected the ATS: the invite is sent as them, under their email limits.
    sender_id: str
    # The candidate's name from the ATS or the API caller, if any: it fills a name not known yet.
    name: str | None = None
    # The API caller's: where to take the candidate back once they've finished, and whether
    # prepza emails them (no invite or reminders when the caller sends them itself).
    return_url: str | None = Field(default=None, max_length=2048)
    sign_in: bool = True


class AtsInviteOut(BaseModel):
    invite_id: UUID
