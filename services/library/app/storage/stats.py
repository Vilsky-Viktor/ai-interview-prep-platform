"""A preparation's public numbers, stored on the set and recounted whenever they change."""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import PreparationRating
from app.models.sets import QuestionSet
from app.models.sharing import JoinedPreparation


def summary_columns() -> tuple:
    rating_avg = QuestionSet.rating_sum * 1.0 / func.nullif(QuestionSet.rating_count, 0)

    return (
        QuestionSet.topic_count.label("topic_count"),
        rating_avg.label("rating_avg"),
        QuestionSet.rating_count.label("rating_count"),
        QuestionSet.join_count.label("join_count"),
    )


async def recount(session: AsyncSession, set_id: uuid.UUID) -> None:
    """Recounts ratings and joins in the caller's transaction, so they can never drift."""
    rated = PreparationRating.set_id == set_id
    await session.execute(
        update(QuestionSet)
        .where(QuestionSet.id == set_id)
        .values(
            rating_sum=select(func.coalesce(func.sum(PreparationRating.value), 0))
            .where(rated)
            .scalar_subquery(),
            rating_count=select(func.count()).where(rated).scalar_subquery(),
            join_count=select(func.count())
            .where(JoinedPreparation.set_id == set_id)
            .scalar_subquery(),
        )
    )
