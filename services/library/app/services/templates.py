from app.helpers.templates import is_indexable
from app.models.sets import QuestionSet
from app.schemas.templates import TemplateSummary
from app.storage import templates


async def summaries(rows: list[QuestionSet]) -> list[TemplateSummary]:
    """Templates as the API lists them, each saying whether its public pages are indexed."""
    duplicates = await templates.duplicate_ids([row.id for row in rows])

    return [
        TemplateSummary.model_validate(row, from_attributes=True).model_copy(
            update={"indexable": is_indexable(row.topic_count, row.id in duplicates)}
        )
        for row in rows
    ]
