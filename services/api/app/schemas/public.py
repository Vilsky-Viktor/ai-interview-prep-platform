from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Interview(BaseModel):
    id: UUID
    title: str | None = Field(
        description="Null while the interview's questions are being generated"
    )
    status: str = Field(description="One of new, in_process or hired")
    ready: bool = Field(description="Whether the questions are ready and candidates can be invited")
    pass_mark: int = Field(description="The minimum grade, in percent, a candidate needs to pass")
    candidate_count: int
    created_at: datetime


class Signals(BaseModel):
    """Integrity signals recorded while the candidate answered.

    They can have innocent causes; never reject a candidate automatically on them.
    """

    tab_leaves: int = Field(description="How many times the candidate left the page")
    copies: int = Field(description="How many times the candidate tried to copy text")
    fast_answers: int = Field(description="Answers given too quickly to have read the question")


class Candidate(BaseModel):
    id: UUID
    email: str
    name: str | None = Field(
        default=None,
        description=(
            "The candidate's name: as given when they were invited, edited by an owner or admin, "
            "or else from their sign-in when they start; null while unknown"
        ),
    )
    status: str = Field(
        description="One of invited, undelivered, in_process, finished, expired or deleted"
    )
    progress: int = Field(description="Percentage of the interview answered")
    grade: int | None = Field(
        description="Final grade in percent; null until the candidate finishes"
    )
    passed: bool | None = Field(
        description=(
            "Whether the grade reached the pass mark; null until the candidate finishes. It "
            "supports a person's decision: don't reject a candidate automatically on it"
        )
    )
    signals: Signals
    results_url: str = Field(description="Link to the candidate's full results in prepza")
    invite_url: str | None = Field(
        default=None,
        description=(
            "The candidate's invite link, to send them yourself if the invite email didn't "
            "arrive; null once they've finished or the invite has expired"
        ),
    )
    created_at: datetime = Field(description="When the invitation was first sent")


class CandidateIn(BaseModel):
    email: EmailStr = Field(description="The candidate's email address")
    name: str | None = Field(
        default=None,
        max_length=200,
        description=(
            "The candidate's name, optional (at most 200 characters). It fills a name not known "
            "yet; inviting the same address again doesn't change a known one"
        ),
    )


class FinishedEvent(BaseModel):
    """The `data` object of a `candidate.finished` or `candidate.rescored` event."""

    interview: Interview
    candidate: Candidate
