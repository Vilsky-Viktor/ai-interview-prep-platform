import uuid

from app.constants.events import ANSWER_RECORDED, SESSION_SCORED
from app.helpers.quality import score_group
from app.services.quality import review
from app.storage import answer_stats


async def handle(event_id: str, event_type: str, data: dict) -> None:
    """Adds one answer, or one finished topic's results, to its questions' statistics, and to
    their bank originals' when they're copies, so an original's signals add up across every test
    that uses it. Each event counts once, however often Pub/Sub delivers it. Other events aren't
    ours."""
    counted = None

    if event_type == ANSWER_RECORDED:
        # Counted only while the question still reads as answered (see RECORD_ANSWER_SQL).
        counted = await answer_stats.record_answer(
            event_id,
            uuid.UUID(data["question_id"]),
            data["question_text"],
            data["option"],
            data["correct"],
        )

    if event_type == SESSION_SCORED:
        counted = await answer_stats.record_results(
            event_id, score_group(data["final_score"]), data["answers"]
        )

    # After the commit: a review never raises, and the next answer repeats a failed one.
    for question_id in counted or []:
        await review(question_id)
