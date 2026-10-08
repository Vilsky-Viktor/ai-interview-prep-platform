from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from prepza_common.constants import MAX_NEWS_TEXT_LENGTH, MAX_NEWS_TITLE_LENGTH
from prepza_common.user import Language
from pydantic import BaseModel, StringConstraints

NewsTitle = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_NEWS_TITLE_LENGTH)
]
NewsText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_NEWS_TEXT_LENGTH)
]


class NewsIn(BaseModel):
    """A post as a superadmin writes it, in English."""

    title: NewsTitle
    text: NewsText
    published_on: date


class NewsOut(BaseModel):
    """A post as the news page shows it, in the reader's language when it's translated."""

    id: UUID
    title: str
    text: str
    published_on: date
    # When the post was last changed, for search engines.
    updated_at: datetime


class AdminNewsOut(NewsOut):
    # Whether every other language has its translation yet.
    translated: bool


class NewsSourceOut(BaseModel):
    """A post to translate (generation): its English text and the languages it lacks."""

    title: str
    text: str
    missing: list[str]


class NewsTranslationIn(BaseModel):
    title: NewsTitle
    text: NewsText


class NewsTranslationsIn(BaseModel):
    """Translations of the post's English `title` and `text`: saved only while the post still
    reads so, since an edit made during translation starts a new one."""

    title: str
    text: str
    translations: dict[Language, NewsTranslationIn]
