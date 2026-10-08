import logging
import time
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status
from prepza_common.encryption import decrypt, encrypt
from prepza_common.notifications import Recipient

from app.config.settings import settings
from app.constants.slack import (
    SLACK_AUTHORIZE_URL,
    SLACK_CALLBACK,
    SLACK_DEFAULT_KINDS,
    SLACK_KINDS,
    SLACK_PAGE,
    SLACK_SCOPE,
    SLACK_STATE_SECONDS,
)
from app.helpers.slack import message, read_state, signed_state
from app.integrations import companies, slack
from app.schemas.slack import SlackOut
from app.storage import slack as storage

logger = logging.getLogger(__name__)


def available() -> bool:
    return bool(
        settings.slack_client_id and settings.slack_client_secret and settings.slack_encryption_key
    )


async def require(company_id: str, user_id: str, editor: bool) -> None:
    """A member may look; only an editor (owner or admin) may change. Others get 404, as if the
    company weren't there; a viewer changing gets 403."""
    try:
        found = await companies.access(company_id, user_id)
    except httpx.HTTPStatusError as error:
        if error.response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found") from None

        raise

    if not found["member"]:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found")

    if editor and not found["editor"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Viewers can't change anything here")


async def overview(company_id: str) -> SlackOut:
    found = await storage.get(company_id)
    kinds = [str(kind) for kind in SLACK_KINDS]

    if found is None:
        return SlackOut(connected=False, kinds=[], all_kinds=kinds)

    return SlackOut(
        connected=True,
        status=found.status,
        team=found.team,
        channel=found.channel,
        kinds=found.kinds,
        all_kinds=kinds,
    )


def start(company_id: str, user_id: str) -> str:
    """Slack's approval page, for the company's editor who pressed "Add to Slack"."""
    if not available():
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Slack isn't set up yet")

    state = signed_state(
        settings.service_secret, company_id, user_id, int(time.time()) + SLACK_STATE_SECONDS
    )
    query = urlencode(
        {
            "client_id": settings.slack_client_id,
            "scope": SLACK_SCOPE,
            "redirect_uri": SLACK_CALLBACK.format(site=settings.site_url),
            "state": state,
        }
    )

    return f"{SLACK_AUTHORIZE_URL}?{query}"


async def finish(code: str | None, state: str, error: str | None) -> str:
    """Back from Slack: the approved channel is saved (replacing an earlier one, whose app is
    removed). Where to send the browser: the company's Slack page, saying how it went."""
    found = read_state(settings.service_secret, state, int(time.time()))

    if found is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This Slack link expired: try again")

    company_id, user_id = found
    page = SLACK_PAGE.format(site=settings.site_url, company_id=company_id)

    if error or not code:
        return f"{page}?slack=cancelled"

    try:
        hook = await slack.exchange(code)
    except (slack.SlackRefused, httpx.HTTPError):
        logger.exception("Couldn't finish connecting Slack for %s", company_id)

        return f"{page}?slack=failed"

    earlier = await storage.get(company_id)
    key = settings.slack_encryption_key
    await storage.connect(
        company_id,
        hook["team"],
        hook["channel"],
        encrypt(key, hook["url"]),
        encrypt(key, hook["token"]),
        earlier.kinds if earlier else [str(kind) for kind in SLACK_DEFAULT_KINDS],
        user_id,
    )

    if earlier is not None:
        await remove_app(earlier.token)

    return f"{page}?slack=connected"


async def set_kinds(company_id: str, kinds: list[str]) -> None:
    if await storage.get(company_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Slack isn't connected")

    chosen = [kind for kind in map(str, SLACK_KINDS) if kind in kinds]
    await storage.set_kinds(company_id, chosen)


async def remove_app(sealed_token: str) -> None:
    token = decrypt(settings.slack_encryption_key, sealed_token)

    if token:
        await slack.revoke(token)


async def disconnect(company_id: str) -> None:
    """Removes prepza's app from the workspace (as far as Slack answers), then the channel."""
    found = await storage.get(company_id)

    if found is not None:
        await remove_app(found.token)
        await storage.remove(company_id)


async def deliver(event: dict, key: str) -> None:
    """A company's notification goes to its Slack channel too, if it chose that kind and whoever
    connected it is still an owner or admin; once per `key` (the bell's), however often its event
    comes. A gone web hook, or a connector no longer an editor, marks the channel for
    reconnecting, and a message Slack refuses is logged: neither is retried. Slack (or the
    companies service) busy or down raises, so Pub/Sub retries the event, backing off, and the
    retry posts it."""
    if event.get("recipient") != Recipient.COMPANY or not available():
        return

    company_id = event["recipient_id"]
    found = await storage.connected(company_id)
    text = message(event, settings.site_url)

    if found is None or event.get("kind") not in found.kinds or text is None:
        return

    # The channel works while whoever connected it is still an owner or admin, like an API key;
    # otherwise an editor reconnects it.
    if not (await companies.access(company_id, found.created_by))["editor"]:
        await storage.mark_broken(company_id)

        return

    webhook = decrypt(settings.slack_encryption_key, found.webhook)

    if webhook is None:
        await storage.mark_broken(company_id)

        return

    # Claimed before posting, so two deliveries of one event at once post it once.
    if not await storage.claim(key):
        return

    try:
        await slack.post(webhook, text)
    except slack.WebhookGone:
        await storage.mark_broken(company_id)
    except slack.SlackRefused as refused:
        logger.warning(
            "Slack refused a %s notification for %s: %s", event["kind"], company_id, refused.error
        )
    except Exception:
        await storage.release(key)

        raise
