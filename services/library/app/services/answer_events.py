import uuid

from app.constants.events import ANSWER_RECORDED
from app.services.quality import review
from app.storage import quality


async def handle(event_type: str, data: dict) -> None:
    """Adds one answer to its question's statistics; other events aren't ours."""
    if event_type == ANSWER_RECORDED:
        question_id = uuid.UUID(data["question_id"])
        await quality.record_answer(
            question_id, data["question_text"], data["option"], data["correct"]
        )
        await review(question_id)
