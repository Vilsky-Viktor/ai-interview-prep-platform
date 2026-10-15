from uuid import UUID

from prepza_common.sets import OptionIn
from prepza_common.titles import Title
from pydantic import BaseModel


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
    title: Title
