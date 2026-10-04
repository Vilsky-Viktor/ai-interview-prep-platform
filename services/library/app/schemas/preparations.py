from datetime import datetime
from uuid import UUID

from prepza_common.constants import MAX_TITLE_LENGTH
from prepza_common.sets import OptionIn
from pydantic import BaseModel, Field, field_validator

from app.constants.sets import Access, Visibility


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
    options: list[OptionIn]


class TopicQuestionsOut(BaseModel):
    """Internal only: a topic with its questions' correct flags."""

    id: UUID
    preparation_id: UUID
    title: str
    questions: list[QuestionOut]
    # Set when the topic is in someone else's public kit: its certificate is paid, its author
    # gets a share, and starting it counts towards the daily limit on new public topics.
    public_author_id: str | None = None


class TopicOut(BaseModel):
    id: UUID
    title: str
    subtopics: list[str]
    question_count: int


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


class MyPreparation(PreparationSummary):
    owned: bool
    # Every topic mastered.
    done: bool


class PreparationDetail(PreparationSummary):
    requirements: list[str]
    topics: list[TopicOut]
    access: Access
    my_rating: int | None
    # Every topic mastered by the viewer; false for anonymous visitors.
    done: bool
    # Stars a rating can give, so the page draws that many.
    rating_scale: int


class VisibilityIn(BaseModel):
    visibility: Visibility


class TitleIn(BaseModel):
    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)

    @field_validator("title")
    @classmethod
    def stripped(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title is required")

        return value
