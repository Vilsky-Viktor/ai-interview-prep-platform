from uuid import UUID

from app.helpers.scores import current_score
from app.integrations import library
from app.storage import progress


async def topic_progress(user_id: str, preparation_id: UUID) -> dict[UUID, tuple[int, int | None]]:
    """Per topic: current questions answered, and the percent correct by the latest answers.

    Answers to a question re-generated since then don't count, as for certificates.
    """
    texts = await library.get_question_texts(preparation_id)

    if texts is None:
        return {}

    scores: dict[UUID, list[int]] = {}

    for row in await progress.for_preparation(user_id, preparation_id):
        if texts.get(str(row.question_id)) == row.question_text:
            scores.setdefault(row.topic_id, []).append(row.score)

    return {topic_id: (len(values), current_score(values)) for topic_id, values in scores.items()}
