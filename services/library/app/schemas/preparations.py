from uuid import UUID

from prepza_common.constants import MAX_TITLE_LENGTH
from prepza_common.sets import OptionIn
from pydantic import BaseModel, Field, field_validator


class CreatedOut(BaseModel):
    id: UUID


class QuestionText(BaseModel):
    """A question as its owner manages it: text, answer options and feedback counts."""

    id: UUID
    text: str
    options: list[OptionIn]
    likes: int = 0
    dislikes: int = 0
    reports: int = 0


class QuestionOut(BaseModel):
    id: UUID
    text: str
    options: list[OptionIn]


class TopicOut(BaseModel):
    id: UUID
    title: str
    subtopics: list[str]
    question_count: int


class TitleIn(BaseModel):
    title: str = Field(min_length=1, max_length=MAX_TITLE_LENGTH)

    @field_validator("title")
    @classmethod
    def stripped(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title is required")

        return value
