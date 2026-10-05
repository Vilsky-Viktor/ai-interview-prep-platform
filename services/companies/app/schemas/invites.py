from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.constants.invites import MAX_BULK_TEXT_LENGTH


class CandidateIn(BaseModel):
    email: EmailStr


class CandidateOut(BaseModel):
    id: UUID
    email: str
    status: str
    progress: int = 0
    grade: int | None = None
    # None until the candidate finishes.
    passed: bool | None = None
    # Integrity signals: page leaves, copy attempts and answers picked too fast to have read.
    tab_leaves: int = 0
    copies: int = 0
    fast_answers: int = 0
    created_at: datetime


class InviteView(BaseModel):
    interview_id: UUID
    title: str | None
    company: str
    logo_url: str | None = None
    # The company's verified domain, for the badge beside its name.
    verified_domain: str | None = None
    email: str
    status: str
    # Shown before the candidate starts: the timer begins at start.
    question_seconds: int


class SessionSummary(BaseModel):
    id: UUID
    topic_title: str
    status: str


class InviteStartOut(BaseModel):
    sessions: list[SessionSummary]


class LinkView(BaseModel):
    """What a test's shareable link shows before anyone starts."""

    title: str | None
    company: str
    logo_url: str | None = None
    verified_domain: str | None = None
    question_seconds: int
    # The signed-in person's invite status for this test; None before they start it.
    status: str | None = None


class LinkIn(BaseModel):
    on: bool


class LinkOut(BaseModel):
    """The test's shareable link code, or None while it's off."""

    link_token: str | None


class CandidateFiltersOut(BaseModel):
    """What a company can narrow its candidates to: statuses and results."""

    filters: list[str]


class BulkInviteIn(BaseModel):
    """A list of emails as pasted or read from a file; any other text around them is ignored."""

    text: str = Field(min_length=1, max_length=MAX_BULK_TEXT_LENGTH)


class SkippedInvite(BaseModel):
    email: str
    # constants/invites.py SkipReason.
    reason: str


class BulkInviteOut(BaseModel):
    invited: list[str]
    skipped: list[SkippedInvite]
