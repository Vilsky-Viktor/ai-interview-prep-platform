from uuid import UUID

from pydantic import BaseModel


class AnswerView(BaseModel):
    answer_id: UUID
    option_index: int
    # None when the candidate may not see results.
    correct: bool | None


class ReviewItem(BaseModel):
    """One question of a round. The correct option only once it's answered."""

    question_id: UUID
    number: int
    text: str
    options: list[str]
    correct_option_index: int | None
    answer: AnswerView | None
