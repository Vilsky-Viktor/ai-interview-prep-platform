from uuid import UUID

from app.integrations import library
from app.storage import progress


async def answered_counts(user_id: str, preparation_id: UUID) -> dict[tuple[UUID, str], int]:
    """Distinct current questions answered per topic and mode, as certificates count them."""
    texts = await library.get_question_texts(preparation_id)

    if texts is None:
        return {}

    counts: dict[tuple[UUID, str], int] = {}

    for row in await progress.for_preparation(user_id, preparation_id):
        if texts.get(str(row.question_id)) == row.question_text:
            key = (row.topic_id, row.mode)
            counts[key] = counts.get(key, 0) + 1

    return counts
