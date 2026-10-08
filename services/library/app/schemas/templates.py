from datetime import datetime
from uuid import UUID

from prepza_common.sets import OptionIn
from pydantic import BaseModel

from app.schemas.preparations import TopicOut


class TemplateSummary(BaseModel):
    """A template in the admin's list."""

    id: UUID
    slug: str | None
    title: str
    level: str
    language: str
    topic_count: int
    created_at: datetime
    # When its title last changed; a sitemap's "last modified".
    updated_at: datetime
    # Whether search engines should index its public pages (helpers/templates.py).
    indexable: bool = False


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


class SampleQuestionOut(BaseModel):
    """A revealed question of a template, with its answer, shown on its public practice page."""

    id: UUID
    topic: str
    text: str
    options: list[OptionIn]
