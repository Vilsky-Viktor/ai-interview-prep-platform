from uuid import UUID

from fastapi import APIRouter, status
from prepza_common.auth import CurrentUser

from app.schemas.manage import ApiSettingsOut, KeyIn, NewKeyOut, NewWebhookOut, WebhookIn
from app.services import manage
from app.services.access import require_company, require_editor

# The company's keys and web hooks, for its API page; not part of the public API.
router = APIRouter(prefix="/manage", tags=["manage"], include_in_schema=False)


@router.get("")
async def get_settings(company_id: UUID, user: CurrentUser) -> ApiSettingsOut:
    """Every member sees the keys (never the keys themselves) and web hooks."""
    await require_company(user, company_id)

    return await manage.overview(company_id)


@router.post("/keys", status_code=status.HTTP_201_CREATED)
async def create_key(company_id: UUID, body: KeyIn, user: CurrentUser) -> NewKeyOut:
    await require_editor(user, company_id)

    return await manage.create_key(company_id, body.name, body.expiry, user.uid)


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_key(company_id: UUID, key_id: UUID, user: CurrentUser) -> None:
    await require_editor(user, company_id)
    await manage.remove_key(company_id, key_id)


@router.post("/webhooks", status_code=status.HTTP_201_CREATED)
async def create_webhook(company_id: UUID, body: WebhookIn, user: CurrentUser) -> NewWebhookOut:
    await require_editor(user, company_id)

    return await manage.create_webhook(company_id, body.url, user.uid)


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_webhook(company_id: UUID, webhook_id: UUID, user: CurrentUser) -> None:
    await require_editor(user, company_id)
    await manage.remove_webhook(company_id, webhook_id)
