import asyncio
import logging
import socket
import time
from datetime import UTC, datetime
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from prepza_common.encryption import decrypt

from app.config.settings import settings
from app.constants.api import RETRY_BATCH, RETRY_GIVE_UP
from app.constants.events import CANDIDATE_FINISHED
from app.helpers.public import candidate_of, interview_of
from app.helpers.webhooks import body_of, public_address, retry_delay, signature
from app.integrations import companies
from app.integrations import webhooks as endpoints
from app.models.api import Webhook, WebhookRetry
from app.schemas.public import FinishedEvent
from app.storage import webhook_retries as retries
from app.storage import webhooks

logger = logging.getLogger(__name__)


async def finished(data: dict, event_id: str) -> None:
    """A candidate finished (companies' candidate.finished): each of the company's web hooks gets
    the interview and the candidate, once, while whoever added it is still an owner or admin.
    Web hooks that already got it are skipped, so a redelivered event reaches only the ones that
    failed. A web hook that doesn't take it is left to the retry job, and the event is done: a
    company's failing endpoint doesn't hold up Pub/Sub for everyone."""
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
    except HTTPException as error:
        # The interview or the candidate is gone since: nothing to tell. Any other refusal
        # (busy, unavailable) raises, so Pub/Sub sends the event again; nothing was sent yet.
        if error.status_code != status.HTTP_404_NOT_FOUND:
            raise

        return

    event = FinishedEvent(
        interview=interview_of(interview),
        candidate=candidate_of(candidate, company_id, interview_id, settings.site_url),
    )
    body = body_of(event_id, CANDIDATE_FINISHED, jsonable_encoder(event))
    # All at once, so slow endpoints together stay within Pub/Sub's acknowledgement deadline.
    taken = await asyncio.gather(*(deliver(hook, event_id, body) for hook in hooks))
    next_at = datetime.now(UTC) + retry_delay(1)

    for hook, ok in zip(hooks, taken, strict=True):
        if not ok:
            await retries.add(hook.id, event_id, body.decode(), next_at)


async def retry() -> int:
    """Every 5 minutes: events web hooks didn't take, whose time came, are sent again, a batch
    at once. One with nowhere to go any more (it got there since, or whoever added the web hook
    is no longer an owner or admin) is dropped. One that fails again waits twice as long; after
    RETRY_GIVE_UP it's dropped and its web hook shows as failing. How many were due."""
    claimed = await retries.claim(RETRY_BATCH)
    # A web hook works while whoever added it is still an owner or admin. Companies not
    # answering fails the run: what it claimed comes back after RETRY_LEASE.
    editors = {}

    for _, hook in claimed:
        maker = (hook.company_id, hook.created_by)

        if maker not in editors:
            editors[maker] = (await companies.access(*maker))["editor"]

    await asyncio.gather(
        *(resend(row, hook, editors[(hook.company_id, hook.created_by)]) for row, hook in claimed)
    )

    return len(claimed)


async def resend(row: WebhookRetry, hook: Webhook, editor: bool) -> None:
    if not editor or await webhooks.delivered(hook.id, row.event_id):
        await retries.remove(hook.id, row.event_id)

        return

    if await deliver(hook, row.event_id, row.body.encode()):
        await retries.remove(hook.id, row.event_id)

        return

    now = datetime.now(UTC)

    if now - row.created_at >= RETRY_GIVE_UP:
        logger.warning("Web hook %s didn't take %s for days: dropped", hook.id, row.event_id)
        await retries.remove(hook.id, row.event_id)
        await webhooks.set_failing(hook.id, True)

        return

    attempts = row.attempts + 1
    await retries.postpone(hook.id, row.event_id, attempts, now + retry_delay(attempts))


async def deliver(hook: Webhook, event_id: str, body: bytes) -> bool:
    """Sends the event to one web hook; whether it took it (one that does no longer shows as
    failing). An address that no longer leads to
    the public internet, or a secret that can't be read, is skipped as taken: retrying can't
    help. An address that doesn't resolve now is a failure, retried like a refused send."""
    secret = decrypt(settings.api_encryption_key, hook.secret)

    try:
        public = await asyncio.to_thread(public_address, hook.url)
    except socket.gaierror as error:
        logger.info(
            "Web hook %s didn't take %s: address lookup failed: %s", hook.id, event_id, error
        )

        return False

    if secret is None or not public:
        logger.warning("Skipped web hook %s: unreadable secret or non-public address", hook.id)

        return True

    try:
        await endpoints.post(hook.url, body, signature(secret, int(time.time()), body))
    except httpx.HTTPError as error:
        logger.info("Web hook %s didn't take %s: %s", hook.id, event_id, error)

        return False

    await webhooks.mark_delivered(hook.id, event_id)

    if hook.failing:
        await webhooks.set_failing(hook.id, False)

    return True
