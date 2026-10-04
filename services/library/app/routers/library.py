from typing import Annotated

from fastapi import APIRouter, Query, Request
from prepza_common.constants import LANGUAGES, LEVELS
from prepza_common.i18n import request_language
from prepza_common.paging import PageParams
from prepza_common.user import Language, Level

from app.constants.library import DEFAULT_LIBRARY_SORT, LibrarySort
from app.helpers.library import default_languages
from app.helpers.preparations import summary_out
from app.schemas.library import LibraryFiltersOut
from app.schemas.preparations import PreparationSummary
from app.storage import search

router = APIRouter(tags=["library"])


@router.get("/library/filters")
async def library_filters(request: Request) -> LibraryFiltersOut:
    """What the library can be filtered and sorted by, and the reader's defaults; public."""
    return LibraryFiltersOut(
        levels=list(LEVELS),
        languages=list(LANGUAGES),
        default_languages=default_languages(request_language(request)),
        sorts=list(LibrarySort),
        default_sort=DEFAULT_LIBRARY_SORT,
    )


@router.get("/library")
async def search_library(
    request: Request,
    page: PageParams,
    q: str = Query(default="", max_length=200),
    level: Level | None = None,
    language: Annotated[list[Language] | None, Query()] = None,
    sort: LibrarySort = DEFAULT_LIBRARY_SORT,
) -> list[PreparationSummary]:
    """Public preparations, a page at a time; no login needed. Without `language`, the reader's
    language and English."""
    languages = language or default_languages(request_language(request))
    rows = await search.search_public(q.strip(), page.offset, page.limit, level, languages, sort)

    return [summary_out(row) for row in rows]
