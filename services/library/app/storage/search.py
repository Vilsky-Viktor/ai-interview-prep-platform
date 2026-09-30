from sqlalchemy import Row, exists, func, or_, select

from app.constants.feedback import RATING_PRIOR_MEAN, RATING_PRIOR_WEIGHT
from app.constants.search import SEARCH_LANGUAGE
from app.constants.sets import SEARCH_LIMIT, SetKind, Visibility
from app.models.sets import QuestionSet, Topic
from app.storage.db import Session
from app.storage.stats import summary_columns


def _matches(text: str):
    topic_hit = exists().where(
        Topic.set_id == QuestionSet.id,
        Topic.search.op("@@")(func.websearch_to_tsquery(SEARCH_LANGUAGE, text)),
    )

    return or_(QuestionSet.title.ilike(f"%{text}%"), topic_hit)


async def search_public(text: str) -> list[Row]:
    """Public preparations whose title or topics match, best rated and most joined first."""
    columns = summary_columns()
    _, rating_avg, rating_count, join_count = columns
    # Bayesian average: few ratings stay close to the prior, many ratings speak for themselves.
    ranked_rating = (
        func.coalesce(rating_avg, 0) * rating_count + RATING_PRIOR_MEAN * RATING_PRIOR_WEIGHT
    ) / (rating_count + RATING_PRIOR_WEIGHT)
    query = select(QuestionSet, *columns).where(
        QuestionSet.kind == SetKind.PREPARATION, QuestionSet.visibility == Visibility.PUBLIC
    )

    if text:
        query = query.where(_matches(text))

    query = query.order_by(
        ranked_rating.desc(),
        join_count.desc(),
        QuestionSet.created_at.desc(),
    ).limit(SEARCH_LIMIT)

    async with Session() as session:
        return list(await session.execute(query))
