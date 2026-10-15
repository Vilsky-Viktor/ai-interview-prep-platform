from datetime import datetime
from typing import Literal
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
    updated_at: datetime | None = Field(
        default=None,
        description=(
            "When it last changed; to sync, pass the last one you got as `updated_since`, with "
            "its `id` as `after`"
        ),
    )


class Signals(BaseModel):
    """Integrity signals recorded while the candidate answered.

    They can have innocent causes; never reject a candidate automatically on them.
    """

    tab_leaves: int = Field(description="How many times the candidate left the page")
    copies: int = Field(description="How many times the candidate tried to copy text")
    fast_answers: int = Field(description="Answers given too quickly to have read the question")


class Section(BaseModel):
    """One section of a candidate's interview."""

    title: str
    grade: int | None = Field(
        default=None, description="The section's grade in percent; null until it's finished"
    )


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
    flagged: bool = Field(
        default=False,
        description=(
            "Whether the integrity signals are too many to trust the result as it is: worth a "
            "person's look at the full results, not a reason to reject"
        ),
    )
    extra_time: int = Field(
        default=0,
        description="Extra time per question the company gave the candidate, in percent",
    )
    sections: list[Section] | None = Field(
        default=None,
        description=(
            "Each section's grade, in order; only when one candidate is read, and in web hook "
            "events (null in lists)"
        ),
    )
    results_url: str = Field(
        description="Link to the candidate's full results and report in prepza"
    )
    invite_url: str | None = Field(
        default=None,
        description=(
            "The candidate's invite link, to send them yourself if the invite email didn't "
            "arrive; null once they've finished or the invite has expired"
        ),
    )
    created_at: datetime = Field(description="When the invitation was first sent")
    updated_at: datetime | None = Field(
        default=None,
        description=(
            "When the candidate last changed (status, name, extra time or result; not the "
            "progress while they answer); to sync, pass the last one you got as `updated_since`, "
            "with its `id` as `after`"
        ),
    )
    started_at: datetime | None = Field(
        default=None, description="When the candidate started; null before"
    )
    finished_at: datetime | None = Field(
        default=None, description="When the candidate finished; null before"
    )


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
    return_url: str | None = Field(
        default=None,
        max_length=2048,
        description=(
            "Where to take the candidate once they've finished, optional: an https address on "
            "the company's verified website domain (or a subdomain of it); see Verified "
            "companies. The finished page shows a button to it, with "
            "`prepza_invite=<candidate id>` added to its query"
        ),
    )
    theme: Literal["light", "dark", "default"] = Field(
        default="default",
        description=(
            "The theme the candidate's pages show, in your company's colors for it: `light` or "
            "`dark` always shows that theme, `default` the candidate's own. A `theme` added to "
            "the `invite_url` (`?theme=dark`) or given to the SDK wins over it"
        ),
    )
    sign_in: bool = Field(
        default=True,
        description=(
            "Whether the candidate signs in to prepza with this email, which prepza sends the "
            "invitation and its reminder to. Set it to false when your platform already knows "
            "who the candidate is and sends them to the response's `invite_url` itself: the "
            "link then opens the interview without signing in, and prepza sends no emails. "
            "Anyone with that link can take the interview, so give it only to the candidate"
        ),
    )


class CandidateEvent(BaseModel):
    """The `data` object of a candidate's event (`candidate.finished`, `candidate.started`,
    `candidate.undelivered`, `candidate.expired`): the interview and the candidate as they are
    when it's sent."""

    interview: Interview
    candidate: Candidate


class RemovedEvent(BaseModel):
    """The `data` object of a `candidate.removed` event: who was removed, as the candidate is
    gone."""

    interview_id: UUID
    candidate_id: UUID
    email: str


class InterviewEvent(BaseModel):
    """The `data` object of an `interview.ready` event."""

    interview: Interview


class TestEvent(BaseModel):
    """The `data` object of a `test` event: empty."""
