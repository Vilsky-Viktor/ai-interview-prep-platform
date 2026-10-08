import httpx
from prepza_common import http

from app.config.settings import settings
from app.constants.slack import (
    SLACK_ACCESS_URL,
    SLACK_CALLBACK,
    SLACK_GONE,
    SLACK_REVOKE_URL,
    SLACK_TIMEOUT_SECONDS,
)


class SlackRefused(Exception):
    """Slack turned the request down; `error` is its reason (e.g. invalid_code)."""

    def __init__(self, error: str) -> None:
        super().__init__(error)
        self.error = error


class WebhookGone(Exception):
    """The channel's web hook no longer works: the app was removed, or the channel is gone."""


async def exchange(code: str) -> dict:
    """The approved code as the company's web hook: {team, channel, url, token}."""
    response = await http.get_client().post(
        SLACK_ACCESS_URL,
        data={
            "client_id": settings.slack_client_id,
            "client_secret": settings.slack_client_secret,
            "code": code,
            "redirect_uri": SLACK_CALLBACK.format(site=settings.site_url),
        },
        timeout=SLACK_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    body = response.json()

    if not body.get("ok"):
        raise SlackRefused(body.get("error", "unknown"))

    hook = body.get("incoming_webhook") or {}

    return {
        "team": (body.get("team") or {}).get("name", ""),
        "channel": hook.get("channel", ""),
        "url": hook["url"],
        "token": body["access_token"],
    }


async def post(webhook: str, text: str) -> None:
    """Posts `text` to the channel; WebhookGone when Slack says the web hook is gone, SlackRefused
    when it turns the message down for good, an httpx.HTTPError when it's busy or down (429, 5xx,
    a timeout), which is worth retrying."""
    response = await http.get_client().post(
        webhook, json={"text": text}, timeout=SLACK_TIMEOUT_SECONDS
    )

    if response.status_code in (403, 404, 410) or response.text.strip() in SLACK_GONE:
        raise WebhookGone

    if response.is_client_error and response.status_code != 429:
        raise SlackRefused(response.text.strip())

    response.raise_for_status()


async def revoke(token: str) -> None:
    """Removes prepza's app from the company's workspace, as far as Slack answers."""
    try:
        await http.get_client().post(
            SLACK_REVOKE_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=SLACK_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError:
        pass
