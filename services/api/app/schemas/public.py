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
    created_at: datetime = Field(description="When the invitation was first sent")


class CandidateIn(BaseModel):
    email: EmailStr = Field(description="The candidate's email address")


class FinishedEvent(BaseModel):
    """The `data` object of a `candidate.finished` event."""

    interview: Interview
    candidate: Candidate
