import asyncio
import socket
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from prepza_common.encryption import encrypt

from app.config.settings import settings
from app.constants.api import KEY_EXPIRY_MONTHS, MAX_KEYS, MAX_WEBHOOKS, KeyExpiry
from app.helpers.keys import add_months, expired, new_key
from app.helpers.webhooks import new_secret, public_address
from app.models.api import ApiKey
from app.schemas.manage import ApiSettingsOut, KeyOut, NewKeyOut, NewWebhookOut, WebhookOut
from app.storage import keys, webhooks


async def overview(company_id: UUID) -> ApiSettingsOut:
    return ApiSettingsOut(
        keys=[key_out(key) for key in await keys.of_company(company_id)],
        webhooks=[
            WebhookOut.model_validate(hook, from_attributes=True)
            for hook in await webhooks.of_company(company_id)
        ],
        expiries=list(KeyExpiry),
    )


def key_out(key: ApiKey) -> KeyOut:
    return KeyOut(
        id=key.id,
        name=key.name,
        shown=key.shown,
        created_at=key.created_at,
        expires_at=key.expires_at,
        expired=expired(key.expires_at, datetime.now(UTC)),
        last_used_at=key.last_used_at,
    )


async def create_key(company_id: UUID, name: str, expiry: KeyExpiry, user_id: str) -> NewKeyOut:
    key, shown, hashed = new_key()
    months = KEY_EXPIRY_MONTHS[expiry]
    expires_at = add_months(datetime.now(UTC), months) if months else None
    row = await keys.add(company_id, name.strip(), shown, hashed, user_id, expires_at, MAX_KEYS)

    if row is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "A company can have up to 10 API keys")

    return NewKeyOut(**key_out(row).model_dump(), key=key)


async def remove_key(company_id: UUID, key_id: UUID) -> None:
    if not await keys.remove(company_id, key_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "API key not found")


async def create_webhook(company_id: UUID, url: str, user_id: str) -> NewWebhookOut:
    """A web hook to an HTTPS address on the public internet, with a new signing secret."""
    if not settings.api_encryption_key:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Web hooks aren't set up yet")

    url = url.strip()

    try:
        address = await asyncio.to_thread(public_address, url)
    except socket.gaierror:
        address = None

    if address is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Use an HTTPS address that's reachable from the internet",
        )

    secret = new_secret()
    sealed = encrypt(settings.api_encryption_key, secret)
    row = await webhooks.add(company_id, url, sealed, user_id, MAX_WEBHOOKS)

    if row is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "A company can have up to 5 web hooks")

    return NewWebhookOut(
        **WebhookOut.model_validate(row, from_attributes=True).model_dump(), secret=secret
    )


async def remove_webhook(company_id: UUID, webhook_id: UUID) -> None:
    if not await webhooks.remove(company_id, webhook_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Web hook not found")
