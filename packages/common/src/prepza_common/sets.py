from uuid import UUID

from prepza_common.constants import DEFAULT_LANGUAGE
from pydantic import BaseModel


class OptionIn(BaseModel):
    answer: str
    correct: bool


class QuestionIn(BaseModel):
    text: str
    options: list[OptionIn]


class TopicIn(BaseModel):
    title: str
    subtopics: list[str]
    questions: list[QuestionIn]
    # Lets later generations find this topic when it's public (library's storage/reuse.py).
    embedding: list[float] | None = None


class PreparationIn(BaseModel):
    """A generated preparation or interview, as generation saves it in library."""

    # Lets library return the same set when a save is retried.
    generation_id: UUID
    owner_uid: str
    source_text: str
    title: str
    level: str
    requirements: list[str]
    topics: list[TopicIn]
    language: str = DEFAULT_LANGUAGE
