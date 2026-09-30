from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class InterviewCreate(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
    mode: str
    share_results: bool = False

    @field_validator("mode")
    @classmethod
    def valid_mode(cls, value: str) -> str:
        if value not in ("open", "choice"):
            raise ValueError("mode must be open or choice")

        return value


class InterviewOut(BaseModel):
    id: UUID
    generation_id: UUID
    set_id: UUID | None
    title: str | None
    mode: str
    share_results: bool
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
    question_limit: int | None = None


class InterviewDetail(InterviewOut):
    topics: list[TopicOut]


class ReviewIn(BaseModel):
    """Topic indices to keep, and optional free-text changes, as the generation service takes them."""

    selected: list[int] = Field(min_length=1)
    instructions: str = ""


class TopicLimitIn(BaseModel):
    limit: int | None = Field(default=None, ge=1)


class InterviewSettings(BaseModel):
    mode: str
    share_results: bool

    @field_validator("mode")
    @classmethod
    def valid_mode(cls, value: str) -> str:
        if value not in ("open", "choice"):
            raise ValueError("mode must be open or choice")

        return value


class TitleIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def stripped(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title is required")

        return value
