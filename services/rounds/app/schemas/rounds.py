from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.constants.rounds import MAX_ANSWER_LENGTH, OPTIONS_PER_QUESTION, Mode, RoundStatus


class RoundCreate(BaseModel):
    topic_id: UUID
    mode: Mode


class AnswerCreate(BaseModel):
    question_id: UUID
    # `text` for open answer rounds, `option_index` for multiple choice rounds.
    text: str | None = Field(default=None, max_length=MAX_ANSWER_LENGTH)
    option_index: int | None = Field(default=None, ge=0, lt=OPTIONS_PER_QUESTION)


class RoundOut(BaseModel):
    id: UUID
    topic_id: UUID
    preparation_id: UUID
    topic_title: str
    mode: Mode
    status: RoundStatus
    total: int
    answered: int
    current_score: int | None
    final_score: int | None
    started_at: datetime
    finished_at: datetime | None
    certificate_id: UUID | None


class TopicPassOut(BaseModel):
    topic_id: UUID
    mode: Mode
    score: int
    answered: int = 0
    certificate_id: UUID | None = None


class MasteredTopicOut(BaseModel):
    preparation_id: UUID
    topic_id: UUID


class NextQuestion(BaseModel):
    """The next unanswered question, without reference answer or correct flags."""

    question_id: UUID
    number: int
    text: str
    options: list[str] | None


class AnswerResult(BaseModel):
    answer_id: UUID
    correct: bool | None
    score: int
    feedback: str | None
    reference_answer: str
    correct_option_index: int | None
    current_score: int
    answered: int
    total: int
