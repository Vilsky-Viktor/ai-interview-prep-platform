import asyncio
import logging
from uuid import UUID

from langchain_core.messages import HumanMessage
from prepza_common.constants import MAX_NEWS_TEXT_LENGTH, MAX_NEWS_TITLE_LENGTH

from app.helpers.prompts import language_name
from app.integrations import library, llm
from app.prompts.news import NEWS_TRANSLATION_PROMPT
from app.schemas.news import NewsSource, TranslatedNews

logger = logging.getLogger(__name__)


async def translate_one(source: NewsSource, language: str) -> TranslatedNews:
    """The post in `language`; raises when the model fails or writes past the post's limits."""
    structured_llm = llm.get_generation_llm().with_structured_output(TranslatedNews)
    prompt = NEWS_TRANSLATION_PROMPT.format(
        language=language_name(language), title=source.title, text=source.text
    )
    result: TranslatedNews = await structured_llm.ainvoke([HumanMessage(content=prompt)])
    title, text = result.title.strip(), result.text.strip()

    if not title or not text:
        raise ValueError(f"Empty {language} translation")

    if len(title) > MAX_NEWS_TITLE_LENGTH or len(text) > MAX_NEWS_TEXT_LENGTH:
        raise ValueError(f"The {language} translation is too long")

    return TranslatedNews(title=title, text=text)


async def translate_news(news_id: UUID) -> None:
    """Translates the post into each language it lacks and saves those that worked. Raises when
    a language failed, so Cloud Tasks runs the job again for the ones still missing; until then
    those languages show the English post. Safe to repeat: a translated language is skipped."""
    source = await library.get_news_source(news_id)

    if source is None or not source.missing:
        return

    results = await asyncio.gather(
        *(translate_one(source, language) for language in source.missing),
        return_exceptions=True,
    )
    done = {}

    for language, result in zip(source.missing, results, strict=True):
        if isinstance(result, BaseException):
            logger.warning("Couldn't translate news post %s into %s: %s", news_id, language, result)
        else:
            done[language] = result

    if done:
        await library.save_news_translations(news_id, source, done)

    if len(done) < len(source.missing):
        raise RuntimeError(f"News post {news_id}: {len(source.missing) - len(done)} languages left")
