import asyncio
import logging
import random
from uuid import UUID

from app.constants.quality import KEY_CHECKS_PER_TOPIC
from app.integrations import library
from app.services.verify import check_key

logger = logging.getLogger(__name__)


async def check_one(question_id: UUID) -> None:
    context = await library.get_question_context(question_id)
    question = await library.get_question_quality(question_id)

    if context is not None and question is not None:
        await check_key(question_id, question, context)


async def check_sample(set_id: UUID) -> None:
    """Before a new test or template is ready, the verifier checks a few random answer keys of
    each topic, and fixes or replaces what's wrong. Never raises: a check that fails mustn't
    fail the generation."""
    try:
        topics = await library.get_question_ids(set_id)
        sample = [
            question_id
            for question_ids in topics
            for question_id in random.sample(
                question_ids, min(KEY_CHECKS_PER_TOPIC, len(question_ids))
            )
        ]
        results = await asyncio.gather(
            *(check_one(question_id) for question_id in sample), return_exceptions=True
        )
    except Exception:
        logger.exception("Couldn't check the answer keys of set %s", set_id)

        return

    for question_id, result in zip(sample, results):
        if isinstance(result, Exception):
            logger.warning("Couldn't check question %s: %s", question_id, result)
