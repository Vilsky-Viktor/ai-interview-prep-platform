import uuid

from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert

from app.models.news import News, NewsTranslation
from app.schemas.news import NewsIn, NewsTranslationIn
from app.storage.db import Session

# Newest first; posts of one day by when they were written.
NEWEST_FIRST = (News.published_on.desc(), News.created_at.desc(), News.id.desc())
# The languages a post is translated into.
OTHER_LANGUAGES = [code for code in LANGUAGES if code != DEFAULT_LANGUAGE]


async def list_news(language: str, offset: int, limit: int) -> list[tuple[News, str, str]]:
    """Posts with their title and text in `language`, or in English while it has no
    translation."""
    query = (
        select(
            News,
            func.coalesce(NewsTranslation.title, News.title),
            func.coalesce(NewsTranslation.text, News.text),
        )
        .outerjoin(
            NewsTranslation,
            (NewsTranslation.news_id == News.id) & (NewsTranslation.language == language),
        )
        .order_by(*NEWEST_FIRST)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return [tuple(row) for row in await session.execute(query)]


async def list_with_counts(offset: int, limit: int) -> list[tuple[News, int]]:
    """Posts with how many translations each has, for the admin zone."""
    counts = (
        select(func.count())
        .where(NewsTranslation.news_id == News.id)
        .correlate(News)
        .scalar_subquery()
    )
    query = select(News, counts).order_by(*NEWEST_FIRST).offset(offset).limit(limit)

    async with Session() as session:
        return [tuple(row) for row in await session.execute(query)]


async def get(news_id: uuid.UUID) -> News | None:
    async with Session() as session:
        return await session.get(News, news_id)


async def create(post: NewsIn) -> News:
    async with Session() as session:
        row = News(**post.model_dump())
        session.add(row)
        await session.commit()
        await session.refresh(row)

        return row


async def update(news_id: uuid.UUID, post: NewsIn) -> tuple[News, bool] | None:
    """Saves the post, and whether its title or text changed: then its translations are
    deleted, and the page shows the English post until it's translated again. None when it's
    gone."""
    async with Session() as session:
        row = await session.get(News, news_id, with_for_update=True)

        if row is None:
            return None

        changed = (row.title, row.text) != (post.title, post.text)

        if changed:
            await session.execute(delete(NewsTranslation).where(NewsTranslation.news_id == news_id))

        row.title, row.text, row.published_on = post.title, post.text, post.published_on
        await session.commit()
        await session.refresh(row)

        return row, changed


async def remove(news_id: uuid.UUID) -> None:
    """Deletes the post with its translations; safe to repeat."""
    async with Session() as session:
        await session.execute(delete(News).where(News.id == news_id))
        await session.commit()


async def missing_languages(news_id: uuid.UUID) -> list[str]:
    query = select(NewsTranslation.language).where(NewsTranslation.news_id == news_id)

    async with Session() as session:
        done = set(await session.scalars(query))

    return [code for code in OTHER_LANGUAGES if code not in done]


async def untranslated() -> list[uuid.UUID]:
    """Posts that lack a translation into some language."""
    query = (
        select(News.id)
        .outerjoin(NewsTranslation)
        .group_by(News.id)
        .having(func.count(NewsTranslation.language) < len(OTHER_LANGUAGES))
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def save_translations(
    news_id: uuid.UUID, title: str, text: str, translations: dict[str, NewsTranslationIn]
) -> None:
    """Saves translations of the post as it reads `title` and `text`; nothing when it changed
    since or is gone. A translation saved again replaces the earlier one. The post's row is
    locked, so an edit can't happen between the check and the save."""
    async with Session() as session:
        row = await session.get(News, news_id, with_for_update=True)

        if row is None or (row.title, row.text) != (title, text):
            return

        for language, translation in translations.items():
            if language == DEFAULT_LANGUAGE:
                continue

            values = {"title": translation.title, "text": translation.text}
            await session.execute(
                insert(NewsTranslation)
                .values(news_id=news_id, language=language, **values)
                .on_conflict_do_update(
                    index_elements=[NewsTranslation.news_id, NewsTranslation.language],
                    set_=values,
                )
            )

        await session.commit()
