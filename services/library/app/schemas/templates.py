from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.preparations import TopicOut


class TemplateSummary(BaseModel):
    """A template in the admin's list."""

    id: UUID
    title: str
    level: str
    language: str
    topic_count: int
    created_at: datetime


class TemplateCopyIn(BaseModel):
    company_id: str


class TemplateCopyOut(BaseModel):
    """The company's new test set."""

    id: UUID
    title: str
    language: str


class TemplateFiltersOut(BaseModel):
    """What the template list can be filtered by."""

    levels: list[str]
    languages: list[str]


class TemplateOut(TemplateSummary):
    topics: list[TopicOut]
