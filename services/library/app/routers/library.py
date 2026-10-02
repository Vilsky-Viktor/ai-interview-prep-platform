from fastapi import APIRouter, Query
from prepza_common.paging import PageParams

from app.helpers.preparations import summary_out
from app.schemas.preparations import PreparationSummary
from app.storage import search

router = APIRouter(tags=["library"])


@router.get("/library")
async def search_library(
    page: PageParams, q: str = Query(default="", max_length=200)
) -> list[PreparationSummary]:
    """Public preparations, a page at a time; no login needed."""
    rows = await search.search_public(q.strip(), page.offset, page.limit)

    return [summary_out(row) for row in rows]
