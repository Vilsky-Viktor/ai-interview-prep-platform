import logging
import uuid

from prepza_common.notifications import NotificationKind

from app.constants.quality import QualityFlag
from app.helpers.notifications import question_notification
from app.helpers.quality import flag_for, no_separation, too_slow
from app.integrations import generation
from app.services import outbox
from app.storage import preparations, quality

logger = logging.getLogger(__name__)


async def mark_wrong(question_id: uuid.UUID) -> None:
    """The test's owner says the marked answer is wrong: flagged at once, and the verifier
    checks it and fixes or replaces the question, as for a flag from answers."""
    await generation.verify_question(question_id, QualityFlag.WRONG_KEY)
    await quality.save_flag(question_id, QualityFlag.WRONG_KEY)


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
            stats is not None and (no_separation(stats) or too_slow(stats)),
        )

        previous = stats.flag if stats else None

        if flag == previous:
            return

        # Saved only once the verifier has it, so a failed call is tried again next time.
        if flag is not None:
            await generation.verify_question(question_id, flag)

        # The owner hears only of a newly flagged question, not of a flag that changes.
        notice = None

        if flag is not None and previous is None:
            question_set = await preparations.get_for_question(question_id)
            topic = await preparations.topic_of_question(question_id)
            notice = question_notification(question_set, topic, NotificationKind.QUESTION_FLAGGED)

        await quality.save_flag(question_id, flag, notice=notice)

        if notice is not None:
            await outbox.flush_quietly()
    except Exception:
        logger.exception("Couldn't review question %s", question_id)
