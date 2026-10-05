from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.review import ReviewItem


class PracticeStartOut(BaseModel):
    """A new practice round: its id, and the first section to open."""

    round_id: UUID
    session_id: UUID


class PracticeTopicResult(BaseModel):
    # The section, for rating and reporting its questions.
    session_id: UUID
    title: str
    # None until the section is finished.
    score: int | None
    review: list[ReviewItem]


class PracticeRoundOut(BaseModel):
    """A talent's round, with every question's right answer once it's finished."""

    round_id: UUID
    template_id: UUID
    title: str | None
    finished: bool
    # The share of the round's questions answered right; None until it's finished.
    grade: int | None
    # Questions the talent picked an answer for (not timed out), and all the round's questions.
    answered: int
    total: int
    started_at: datetime
    # The first section still open, to continue an unfinished round.
    open_session_id: UUID | None
    topics: list[PracticeTopicResult]


class PracticeRoundSummary(BaseModel):
    round_id: UUID
    started_at: datetime
    finished: bool
    # The share of the round's questions answered, in percent.
    progress: int
    grade: int | None


class PracticeTopicProgress(BaseModel):
    """How far the talent got on one of the template's topics in their latest round."""

    topic_id: UUID
    answered: int
    total: int


class PracticeSizeOut(BaseModel):
    """How many questions a practice round on the template has."""

    questions: int
