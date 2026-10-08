from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.constants.notifications import MAX_COMPANIES_PER_CALL


class CompanyIdsIn(BaseModel):
    company_ids: list[UUID] = Field(max_length=MAX_COMPANIES_PER_CALL)


class MemberBriefOut(BaseModel):
    user_id: str
    # An owner or admin, who can act on reminders (top up, invite); a viewer only looks.
    editor: bool


class CompanyMembersOut(BaseModel):
    id: UUID
    name: str
    # Members who joined, in any role; pending invites have no user yet.
    members: list[MemberBriefOut]


class CompaniesMembersOut(BaseModel):
    companies: list[CompanyMembersOut]


class WaitingInterviewOut(BaseModel):
    id: UUID
    company_id: UUID
    title: str | None
    generation_id: UUID | None
    created_at: datetime


class WaitingInterviewsOut(BaseModel):
    # Ready, and nobody was invited yet.
    without_candidates: list[WaitingInterviewOut]
    # Still waiting for their questions (generation knows whether for a topics' review).
    being_generated: list[WaitingInterviewOut]
