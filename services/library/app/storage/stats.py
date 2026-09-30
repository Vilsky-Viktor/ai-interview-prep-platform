"""Correlated subqueries with the public numbers of a preparation."""

from sqlalchemy import func, select

from app.models.feedback import PreparationRating
from app.models.sets import QuestionSet, Topic
from app.models.sharing import JoinedPreparation


def summary_columns() -> tuple:
    topic_count = select(func.count(Topic.id)).where(Topic.set_id == QuestionSet.id)
    rating_avg = select(func.avg(PreparationRating.value)).where(
        PreparationRating.set_id == QuestionSet.id
    )
    rating_count = select(func.count()).where(PreparationRating.set_id == QuestionSet.id)
    join_count = select(func.count()).where(JoinedPreparation.set_id == QuestionSet.id)

    # Correlate only with the preparation, even when the outer query joins these tables.
    return (
        topic_count.correlate(QuestionSet).scalar_subquery().label("topic_count"),
        rating_avg.correlate(QuestionSet).scalar_subquery().label("rating_avg"),
        rating_count.correlate(QuestionSet).scalar_subquery().label("rating_count"),
        join_count.correlate(QuestionSet).scalar_subquery().label("join_count"),
    )
