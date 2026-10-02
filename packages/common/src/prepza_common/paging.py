from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query
from prepza_common.constants import MAX_PAGE_SIZE


@dataclass
class Page:
    offset: int
    limit: int


def page(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = MAX_PAGE_SIZE,
) -> Page:
    """`?offset=&limit=`; without them, the first full page."""
    return Page(offset=offset, limit=limit)


PageParams = Annotated[Page, Depends(page)]
