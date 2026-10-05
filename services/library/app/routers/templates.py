from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from prepza_common.constants import LANGUAGES, LEVELS, MAX_TITLE_LENGTH
from prepza_common.paging import PageParams
from prepza_common.user import Language, Level

from app.constants.sets import SetKind
from app.schemas.preparations import TopicOut
from app.schemas.templates import TemplateFiltersOut, TemplateOut, TemplateSummary
from app.storage import preparations, templates

# Templates: public, for the practice pages search engines index and for companies to start a
# test from. Topics only, never the questions; only superadmins change them.
router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/filters")
async def template_filters() -> TemplateFiltersOut:
    return TemplateFiltersOut(levels=list(LEVELS), languages=list(LANGUAGES))


@router.get("")
async def list_templates(
    page: PageParams,
    q: str = Query(default="", max_length=MAX_TITLE_LENGTH),
    level: Level | None = None,
    language: Annotated[list[Language] | None, Query()] = None,
) -> list[TemplateSummary]:
    rows = await templates.list_templates(q.strip(), level, language or [], page.offset, page.limit)

    return [TemplateSummary.model_validate(row, from_attributes=True) for row in rows]


@router.get("/{template_id}")
async def get_template(template_id: UUID) -> TemplateOut:
    """A template's topics and subtopics, to review before using it; its questions stay hidden."""
    template = await preparations.get(template_id)

    if template is None or template.kind != SetKind.TEMPLATE:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

    topics = await preparations.get_topics(template_id)

    return TemplateOut(
        **TemplateSummary.model_validate(template, from_attributes=True).model_dump(),
        topics=[
            TopicOut(
                id=topic.id, title=topic.title, subtopics=topic.subtopics, question_count=count
            )
            for topic, count in topics
        ],
    )
