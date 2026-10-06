import logging
import uuid

from app.constants.events import ANSWER_RECORDED, SESSION_SCORED
from app.constants.quality import MIN_ANSWERS
from app.helpers.quality import score_group
from app.services.quality import review
from app.storage import answer_stats

logger = logging.getLogger(__name__)


async def handle(event_id: str, event_type: str, data: dict) -> None:
    """Adds one answer, or one finished topic's results, to its questions' statistics, and to
    their bank originals' when they're copies, so an original's signals add up across every test
    that uses it. Each event counts once, however often Pub/Sub delivers it. Other events aren't
    ours."""
    counted = None

    # The payload is read before anything is stored: a malformed event is logged and dropped,
    # since a retry would fail the same way until it's dead-lettered.
    try:
        if event_type == ANSWER_RECORDED:
            answer = (
                uuid.UUID(data["question_id"]),
                data["question_text"],
                data["option"],
                data["correct"],
            )

        if event_type == SESSION_SCORED:
            results = (score_group(data["final_score"]), list(data["answers"]))
    except (KeyError, TypeError, ValueError) as error:
        logger.error("Dropped malformed %s event %s: %r", event_type, event_id, error)

        return

    if event_type == ANSWER_RECORDED:
        # Counted only while the question still reads as answered (see RECORD_ANSWER_SQL).
        shown = await answer_stats.record_answer(event_id, *answer)
        # Answers say nothing about a question shown fewer than MIN_ANSWERS times (flag_for,
        # too_slow), so its review would come out as the last one did: it's skipped.
        counted = [
            question_id for question_id, times in (shown or {}).items() if times >= MIN_ANSWERS
        ]

    if event_type == SESSION_SCORED:
        counted = await answer_stats.record_results(event_id, *results)

    # After the commit: a review never raises, and the question's next event repeats a failed
    # one.
    for question_id in counted or []:
        await review(question_id)
