import logging

from pydantic import ValidationError

from app.config.settings import settings
from app.constants.generation import MAX_OUTPUT_TOKENS
from app.constants.quality import BATCH_RETRY_STATUSES
from app.integrations import library, openai_batch
from app.models.key_checks import KeyCheck as KeyCheckRow
from app.schemas.verify import KeyCheck
from app.services.verify import apply_key_check, check_key, key_check_prompt
from app.storage import key_checks

logger = logging.getLogger(__name__)


def request_body(prompt: str) -> dict:
    return {
        "model": settings.generation_model,
        "reasoning_effort": settings.verify_reasoning_effort,
        "max_completion_tokens": MAX_OUTPUT_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "key_check", "schema": KeyCheck.model_json_schema()},
        },
    }


async def current(check: KeyCheckRow):
    """The question and its context, or None when it was deleted or changed since flagged."""
    context = await library.get_question_context(check.question_id)
    question = await library.get_question_quality(check.question_id)

    if context is None or question is None or question.text != check.question_text:
        return None

    return question, context


async def submit_pending() -> None:
    """Sends every waiting key check as one batch."""
    requests = {}
    sent = []
    gone = []

    for check in await key_checks.unsent():
        found = await current(check)

        if found is None:
            gone.append(check.question_id)
        else:
            requests[str(check.question_id)] = request_body(key_check_prompt(*found))
            sent.append(check)

    if gone:
        await key_checks.remove(gone)

    if requests:
        batch_id = await openai_batch.submit(requests)
        await key_checks.set_batch([check.question_id for check in sent], batch_id)
        logger.info("Sent %d key checks in batch %s", len(requests), batch_id)


async def apply_reply(check: KeyCheckRow, reply: str | None) -> None:
    found = await current(check)

    if found is None:
        return

    question, context = found

    try:
        result = KeyCheck.model_validate_json(reply) if reply else None
    except ValidationError:
        result = None

    # A request that failed in the batch is checked right away instead.
    if result is None:
        await check_key(check.question_id, question, context)
    else:
        await apply_key_check(check.question_id, question, context, result)


async def collect_finished() -> None:
    """Applies the results of finished batches; failed or expired ones are sent again."""
    for batch_id in await key_checks.sent_batches():
        status, output_file_id = await openai_batch.status(batch_id)
        checks = await key_checks.in_batch(batch_id)

        if status in BATCH_RETRY_STATUSES:
            await key_checks.set_batch([check.question_id for check in checks], None)

            continue

        if status != "completed":
            continue

        replies = await openai_batch.results(output_file_id) if output_file_id else {}

        for check in checks:
            try:
                await apply_reply(check, replies.get(str(check.question_id)))
            except Exception:
                logger.exception("Key check of question %s failed", check.question_id)
                await key_checks.set_batch([check.question_id], None)

                continue

            await key_checks.remove([check.question_id])
