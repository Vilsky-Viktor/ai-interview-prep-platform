from sqlalchemy import Row, exists, func, or_, select

from app.constants.feedback import RATING_PRIOR_MEAN, RATING_PRIOR_WEIGHT
from app.constants.search import SEARCH_LANGUAGE
from app.constants.sets import SetKind, Visibility
from app.models.sets import QuestionSet, Topic
from app.storage.db import Session
from app.storage.stats import summary_columns


def _matches(text: str):
    topic_hit = exists().where(
        Topic.set_id == QuestionSet.id,
        Topic.search.op("@@")(func.websearch_to_tsquery(SEARCH_LANGUAGE, text)),
    )

    return or_(QuestionSet.title.ilike(f"%{text}%"), topic_hit)


async def search_public(text: str, offset: int, limit: int) -> list[Row]:
    """Public preparations whose title or topics match, best rated and most joined first."""
    # Bayesian average: few ratings stay close to the prior, many ratings speak for themselves.
    ranked_rating = (QuestionSet.rating_sum + RATING_PRIOR_MEAN * RATING_PRIOR_WEIGHT) / (
        QuestionSet.rating_count + RATING_PRIOR_WEIGHT
    )
    query = select(QuestionSet, *summary_columns()).where(
        QuestionSet.kind == SetKind.PREPARATION, QuestionSet.visibility == Visibility.PUBLIC
    )

    if text:
        query = query.where(_matches(text))

    # The id breaks ties, so pages never overlap or skip a preparation.
    query = (
        query.order_by(
            ranked_rating.desc(),
            QuestionSet.join_count.desc(),
            QuestionSet.created_at.desc(),
            QuestionSet.id,
        )
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.execute(query))
