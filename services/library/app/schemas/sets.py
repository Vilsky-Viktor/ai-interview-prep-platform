from uuid import UUID

from pydantic import BaseModel

from app.schemas.preparations import QuestionOut, TopicOut


class SetOut(BaseModel):
    id: UUID
    kind: str
    owner_id: str
    title: str
    level: str
    language: str
    topics: list[TopicOut]


class SetTopicOut(BaseModel):
    id: UUID
    title: str
    questions: list[QuestionOut]


class SetContent(BaseModel):
    """Internal: every question of an interview, with answers."""

    id: UUID
    title: str
    topics: list[SetTopicOut]
