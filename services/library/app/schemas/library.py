from pydantic import BaseModel

from app.constants.library import LibrarySort


class LibraryFiltersOut(BaseModel):
    """What the library page can filter and sort by, and what it starts with."""

    levels: list[str]
    languages: list[str]
    default_languages: list[str]
    sorts: list[LibrarySort]
    default_sort: LibrarySort
