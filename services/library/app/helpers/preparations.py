from sqlalchemy import Row

from app.schemas.preparations import PreparationSummary


def summary_out(row: Row) -> PreparationSummary:
    """Builds a summary from a `QuestionSet` row with the `summary_columns()` numbers."""
    item, topic_count, rating_avg, rating_count, join_count = row

    return PreparationSummary(
        id=item.id,
        title=item.title,
        level=item.level,
        visibility=item.visibility,
        created_at=item.created_at,
        topic_count=topic_count,
        rating_avg=round(float(rating_avg), 1) if rating_avg is not None else None,
        rating_count=rating_count,
        join_count=join_count,
    )
