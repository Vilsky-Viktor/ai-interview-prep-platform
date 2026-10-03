from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.constants.interviews import (
    DEFAULT_QUESTION_SECONDS,
    MAX_QUESTION_SECONDS,
    MIN_QUESTION_SECONDS,
)


class InterviewCreate(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)


class InterviewOut(BaseModel):
    id: UUID
    generation_id: UUID
    set_id: UUID | None
    title: str | None
    question_seconds: int
    candidate_count: int
    created_at: datetime


class QuestionText(BaseModel):
    id: UUID
    text: str
    likes: int
    dislikes: int
    reports: int


class ReportOut(BaseModel):
    id: UUID
    reason: str
    comment: str
    created_at: datetime


class TopicOut(BaseModel):
    id: UUID
    title: str
    subtopics: list[str] = []
    question_count: int
    question_limit: int | None


class InterviewDetail(InterviewOut):
    topics: list[TopicOut]


class ReviewIn(BaseModel):
    """Topic indices to keep, and optional free-text changes, as the generation service takes them."""

    selected: list[int] = Field(min_length=1)
    instructions: str = ""
    # Every drafted topic with the reviewer's own edits; generation validates it.
    topics: list[dict] | None = None


class TopicLimitIn(BaseModel):
    limit: int | None = Field(default=None, ge=1)


class InterviewSettings(BaseModel):
    question_seconds: int = Field(
        default=DEFAULT_QUESTION_SECONDS, ge=MIN_QUESTION_SECONDS, le=MAX_QUESTION_SECONDS
    )


class TitleIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def stripped(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title is required")

        return value
