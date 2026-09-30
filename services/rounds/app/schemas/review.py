from uuid import UUID

from pydantic import BaseModel


class AnswerView(BaseModel):
    answer_id: UUID
    text: str | None
    option_index: int | None
    correct: bool | None
    score: int
    feedback: str | None


class ReviewItem(BaseModel):
    """One question of a round. Reference answer and correct option only once it's answered."""

    question_id: UUID
    number: int
    text: str
    options: list[str] | None
    reference_answer: str | None
    correct_option_index: int | None
    answer: AnswerView | None
