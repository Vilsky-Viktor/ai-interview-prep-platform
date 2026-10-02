import logging
import uuid

from app.helpers.quality import flag_for
from app.integrations import generation
from app.storage import quality

logger = logging.getLogger(__name__)


async def review(question_id: uuid.UUID) -> None:
    """Flags a question from its answers and feedback, and sends a new flag to the verifier.

    Never raises: a failed review is repeated by the question's next answer or feedback.
    """
    try:
        found = await quality.load(question_id)

        if found is None:
            return

        question, stats, reports, likes, dislikes = found

        if stats is not None and stats.kept:
            return

        flag = flag_for(
            question.options,
            stats.answers if stats else 0,
            stats.correct if stats else 0,
            stats.option_picks if stats else {},
            reports,
            likes,
            dislikes,
        )

        if flag == (stats.flag if stats else None):
            return

        # Saved only once the verifier has it, so a failed call is tried again next time.
        if flag is not None:
            await generation.verify_question(question_id, flag)

        await quality.save_flag(question_id, flag)
    except Exception:
        logger.exception("Couldn't review question %s", question_id)
