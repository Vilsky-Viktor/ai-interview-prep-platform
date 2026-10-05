from datetime import datetime
from uuid import UUID

from prepza_common.constants import MAX_GOAL_LENGTH, MAX_TITLE_LENGTH
from prepza_common.user import Language
from pydantic import BaseModel, Field, field_validator

from app.constants.interviews import (
    DEFAULT_PASS_MARK,
    DEFAULT_QUESTION_SECONDS,
    MAX_PASS_MARK,
    MAX_QUESTION_SECONDS,
    MIN_PASS_MARK,
    MIN_QUESTION_SECONDS,
)


class InterviewCreate(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_GOAL_LENGTH)
    # The language to generate the interview in; none means the job description's own.
    generate_in: Language | None = None


class InterviewFromTemplate(BaseModel):
    template_id: UUID


class PreviewOut(BaseModel):
    """The first session of a member's preview, to open in the player."""

    session_id: UUID


class InterviewOut(BaseModel):
    id: UUID
    # None for a test made from a template.
    generation_id: UUID | None
    set_id: UUID | None
    title: str | None
    question_seconds: int
    candidate_count: int
    hired: bool
    pass_mark: int
    # The shareable link's code while it's on.
    link_token: str | None
    # New, in process or hired (constants/interviews.py).
    status: str
    created_at: datetime


class QuestionOption(BaseModel):
    answer: str
    correct: bool


class QuestionText(BaseModel):
    """A question as the company manages it: text, answer options and feedback counts."""

    id: UUID
    text: str
    options: list[QuestionOption]
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
    # Questions each candidate gets from the topic.
    question_limit: int


class InterviewDetail(InterviewOut):
    topics: list[TopicOut]


class ReviewIn(BaseModel):
    """Topic indices to keep, and optional free-text changes, as the generation service takes them."""

    selected: list[int] = Field(min_length=1)
    instructions: str = ""
    # Every drafted topic with the reviewer's own edits; generation validates it.
    topics: list[dict] | None = None


class TopicLimitIn(BaseModel):
    # The topic's whole size gives every candidate every question.
    limit: int = Field(ge=1)


class InterviewSettings(BaseModel):
    question_seconds: int = Field(
        default=DEFAULT_QUESTION_SECONDS, ge=MIN_QUESTION_SECONDS, le=MAX_QUESTION_SECONDS
    )
    hired: bool = False
    pass_mark: int = Field(default=DEFAULT_PASS_MARK, ge=MIN_PASS_MARK, le=MAX_PASS_MARK)


class TitleIn(BaseModel):
    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)

    @field_validator("title")
    @classmethod
    def stripped(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title is required")

        return value
