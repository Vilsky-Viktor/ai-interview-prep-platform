from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.constants.rounds import OPTIONS_PER_QUESTION, RoundStatus


class RoundCreate(BaseModel):
    topic_id: UUID


class AnswerCreate(BaseModel):
    question_id: UUID
    option_index: int = Field(ge=0, lt=OPTIONS_PER_QUESTION)


class RoundOut(BaseModel):
    id: UUID
    topic_id: UUID
    preparation_id: UUID
    topic_title: str
    status: RoundStatus
    total: int
    answered: int
    current_score: int | None
    final_score: int | None
    # Whether the score shown passes: the final one once finished, the running one before.
    passed: bool | None
    started_at: datetime
    finished_at: datetime | None
    certificate_id: UUID | None


class TopicProgressOut(BaseModel):
    """How far the user is towards the topic's certificate.

    `answered` counts distinct current questions; `score` is the percent of them answered
    correctly, by the latest answer to each. `in_progress` is true while a round is unfinished.
    """

    topic_id: UUID
    answered: int
    score: int | None
    # Every question of the topic answered, and whether the topic passes (certified, or complete
    # with a passing score).
    complete: bool
    passed: bool
    certificate_id: UUID | None = None
    in_progress: bool = False


class NextQuestion(BaseModel):
    """The next unanswered question, without the correct flags."""

    question_id: UUID
    number: int
    text: str
    options: list[str]


class AnswerResult(BaseModel):
    answer_id: UUID
    correct: bool
    correct_option_index: int
    current_score: int
    passed: bool
    answered: int
    total: int
