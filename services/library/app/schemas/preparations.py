from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.constants.sets import Access, Visibility


class OptionIn(BaseModel):
    answer: str
    correct: bool


class QuestionIn(BaseModel):
    text: str
    reference_answer: str
    options: list[OptionIn]


class TopicIn(BaseModel):
    title: str
    subtopics: list[str]
    questions: list[QuestionIn]


class PreparationIn(BaseModel):
    owner_uid: str
    source_text: str
    title: str
    level: str
    requirements: list[str]
    topics: list[TopicIn]


class CreatedOut(BaseModel):
    id: UUID


class QuestionText(BaseModel):
    id: UUID
    text: str
    likes: int = 0
    dislikes: int = 0
    reports: int = 0


class QuestionOut(BaseModel):
    id: UUID
    text: str
    reference_answer: str
    options: list[OptionIn]


class TopicQuestionsOut(BaseModel):
    """Internal only: a topic with reference answers and correct flags."""

    id: UUID
    preparation_id: UUID
    title: str
    question_limit: int | None = None
    questions: list[QuestionOut]


class TopicOut(BaseModel):
    id: UUID
    title: str
    subtopics: list[str]
    question_count: int
    question_limit: int | None = None


class TopicLimitIn(BaseModel):
    limit: int | None = Field(default=None, ge=1)


class PreparationSummary(BaseModel):
    id: UUID
    title: str
    level: str
    visibility: str
    created_at: datetime
    topic_count: int
    rating_avg: float | None
    rating_count: int
    join_count: int


class PreparationDetail(PreparationSummary):
    requirements: list[str]
    topics: list[TopicOut]
    access: Access
    my_rating: int | None


class VisibilityIn(BaseModel):
    visibility: Visibility


class TitleIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def stripped(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title is required")

        return value
