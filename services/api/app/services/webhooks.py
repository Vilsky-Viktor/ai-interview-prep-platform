import asyncio
import logging
import time
from uuid import UUID

import httpx
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from prepza_common.encryption import decrypt

from app.config.settings import settings
from app.constants.events import CANDIDATE_FINISHED
from app.helpers.public import candidate_of, interview_of
from app.helpers.webhooks import body_of, public_address, signature
from app.integrations import companies
from app.integrations import webhooks as endpoints
from app.schemas.public import FinishedEvent
from app.storage import webhooks

logger = logging.getLogger(__name__)


class DeliveryFailed(Exception):
    """Some web hooks didn't take the event: raised so Pub/Sub sends it again, with backoff."""


async def finished(data: dict, event_id: str) -> None:
    """A candidate finished (companies' candidate.finished): each of the company's web hooks gets
    the interview and the candidate, once, while whoever added it is still an owner or admin. Web hooks that already got it are skipped, so a
    redelivered event reaches only the ones that failed."""
    company_id = UUID(data["company_id"])
    hooks = [
        hook
        for hook in await webhooks.of_company(company_id)
        if not await webhooks.delivered(hook.id, event_id)
    ]
    # A web hook works while whoever added it is still an owner or admin, like an API key.
    editors = {
        maker: (await companies.access(company_id, maker))["editor"]
        for maker in {hook.created_by for hook in hooks}
    }
    hooks = [hook for hook in hooks if editors[hook.created_by]]

    if not hooks:
        return

    interview_id, invite_id = UUID(data["interview_id"]), UUID(data["candidate_invite_id"])

    try:
        interview = await companies.interview(company_id, interview_id)
        candidate = await companies.candidate(company_id, interview_id, invite_id)
    except HTTPException:
        # The interview or the candidate is gone since: nothing to tell.
        return

    event = FinishedEvent(
        interview=interview_of(interview),
        candidate=candidate_of(candidate, company_id, interview_id, settings.site_url),
    )
    body = body_of(event_id, CANDIDATE_FINISHED, jsonable_encoder(event))
    # All at once, so slow endpoints together stay within Pub/Sub's acknowledgement deadline.
    taken = await asyncio.gather(*(deliver(hook, event_id, body) for hook in hooks))
    failed = [hook.url for hook, ok in zip(hooks, taken, strict=True) if not ok]

    if failed:
        raise DeliveryFailed(f"Web hooks didn't take {event_id}: {', '.join(failed)}")


async def deliver(hook, event_id: str, body: bytes) -> bool:
    """Sends the event to one web hook; whether it took it. An address that no longer leads to
    the public internet, or a secret that can't be read, is skipped as taken: retrying can't
    help."""
    secret = decrypt(settings.api_encryption_key, hook.secret)

    if secret is None or not await asyncio.to_thread(public_address, hook.url):
        logger.warning("Skipped web hook %s: unreadable secret or non-public address", hook.id)

        return True

    try:
        await endpoints.post(hook.url, body, signature(secret, int(time.time()), body))
    except httpx.HTTPError as error:
        logger.info("Web hook %s didn't take %s: %s", hook.id, event_id, error)

        return False

    await webhooks.mark_delivered(hook.id, event_id)

    return True
