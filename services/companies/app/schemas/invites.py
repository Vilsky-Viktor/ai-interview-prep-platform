from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.constants.invites import (
    EXTRA_TIME_OPTIONS,
    MAX_BULK_TEXT_LENGTH,
    MAX_CANDIDATE_NAME_LENGTH,
)


class CandidateIn(BaseModel):
    email: EmailStr
    # Optional; trimmed and cut to MAX_CANDIDATE_NAME_LENGTH as it's saved.
    name: str | None = None


class CandidateOut(BaseModel):
    id: UUID
    email: str
    # The name from the candidate's sign-in; None until they start, or when it has none.
    name: str | None = None
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


class CompanyCandidateOut(CandidateOut):
    """A candidate found across the company's interviews, with the interview they're in."""

    interview_id: UUID
    interview_title: str | None


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
    # The form's name field, for a text with one email; trimmed and cut as it's saved.
    name: str | None = None


class SkippedInvite(BaseModel):
    email: str
    # constants/invites.py SkipReason.
    reason: str


class BulkInviteOut(BaseModel):
    invited: list[str]
    skipped: list[SkippedInvite]


class ExtraTimeIn(BaseModel):
    """Extra time for a candidate who needs it, in percent of each question's time."""

    extra_time: int

    @field_validator("extra_time")
    @classmethod
    def offered(cls, value: int) -> int:
        if value not in EXTRA_TIME_OPTIONS:
            raise ValueError(f"Extra time must be one of {EXTRA_TIME_OPTIONS}")

        return value


class CandidateNameIn(BaseModel):
    """A candidate's name as an owner or admin corrects it; blank means not known."""

    name: str = Field(max_length=MAX_CANDIDATE_NAME_LENGTH)

    @field_validator("name")
    @classmethod
    def stripped(cls, value: str) -> str:
        return value.strip()


class InvitedCompaniesOut(BaseModel):
    """The companies that invited an address, for the notifications service."""

    company_ids: list[str]
