from fastapi import APIRouter, Query

from app.helpers.preparations import summary_out
from app.schemas.preparations import PreparationSummary
from app.storage import search

router = APIRouter(tags=["library"])


@router.get("/library")
async def search_library(q: str = Query(default="", max_length=200)) -> list[PreparationSummary]:
    """Public preparations; no login needed."""
    return [summary_out(row) for row in await search.search_public(q.strip())]
