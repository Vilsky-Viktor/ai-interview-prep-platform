from uuid import UUID

from pydantic import BaseModel


class AnswerView(BaseModel):
    answer_id: UUID
    # None when a timed question ran out first.
    option_index: int | None
    # None when the candidate may not see results.
    correct: bool | None
    # Seconds the answer took; interview answers only.
    seconds: int | None = None
    # Answered faster than FAST_ANSWER_SECONDS.
    fast: bool = False


class ReviewItem(BaseModel):
    """One question of a round. The correct option only once it's answered."""

    question_id: UUID
    number: int
    text: str
    options: list[str]
    correct_option_index: int | None
    answer: AnswerView | None
