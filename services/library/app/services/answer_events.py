import uuid

from app.constants.events import ANSWER_RECORDED, SESSION_SCORED
from app.helpers.quality import score_group
from app.services.quality import review
from app.storage import quality


async def handle(event_type: str, data: dict) -> None:
    """Adds one answer, or one finished topic's results, to its questions' statistics, and to
    their bank originals' when they're copies, so an original's signals add up across every test
    that uses it. Other events aren't ours."""
    if event_type == ANSWER_RECORDED:
        question_id = uuid.UUID(data["question_id"])
        source_id = await quality.source_of(question_id)

        for answered in (question_id, source_id):
            if answered is None:
                continue

            # Counted only while the question still reads as answered (see record_answer).
            await quality.record_answer(
                answered, data["question_text"], data["option"], data["correct"]
            )
            await review(answered)

    if event_type == SESSION_SCORED:
        group = score_group(data["final_score"])

        for result in data["answers"]:
            question_id = uuid.UUID(result["question_id"])
            source_id = await quality.source_of(question_id)

            for counted in (question_id, source_id):
                if counted is None:
                    continue

                await quality.record_result(
                    counted,
                    result["question_text"],
                    group,
                    result["correct"],
                    result["timed_out"],
                )
                await review(counted)
