from uuid import UUID

from pydantic import BaseModel, Field

from app.constants.rounds import OPTIONS_PER_QUESTION


class AnswerCreate(BaseModel):
    question_id: UUID
    option_index: int = Field(ge=0, lt=OPTIONS_PER_QUESTION)


class NextQuestion(BaseModel):
    """The next unanswered question, without the correct flags."""

    question_id: UUID
    number: int
    text: str
    options: list[str]
    # Timed interviews only: seconds until the question counts as wrong. Relative, so the
    # candidate's clock being off doesn't matter.
    seconds_left: float | None = None
