from uuid import UUID

from pydantic import BaseModel, EmailStr


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


class AtsInviteOut(BaseModel):
    invite_id: UUID
