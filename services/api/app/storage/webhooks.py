import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.api import DELIVERIES_KEPT
from app.models.api import Webhook, WebhookDelivery
from app.storage.db import Session


async def of_company(company_id: uuid.UUID) -> list[Webhook]:
    """Oldest first."""
    query = select(Webhook).where(Webhook.company_id == company_id).order_by(Webhook.created_at)

    async with Session() as session:
        return list(await session.scalars(query))


async def add(
    company_id: uuid.UUID, url: str, sealed_secret: str, user_id: str, limit: int
) -> Webhook | None:
    """None when the company already has `limit` web hooks. One company's web hooks are added
    one at a time, so two at once can't both pass the count."""
    count = select(func.count()).select_from(Webhook).where(Webhook.company_id == company_id)
    hook = Webhook(company_id=company_id, url=url, secret=sealed_secret, created_by=user_id)

    async with Session() as session:
        await session.execute(
            select(func.pg_advisory_xact_lock(func.hashtext(f"webhooks:{company_id}")))
        )

        if await session.scalar(count) >= limit:
            return None

        session.add(hook)
        await session.commit()
        await session.refresh(hook)

    return hook


async def remove(company_id: uuid.UUID, webhook_id: uuid.UUID) -> bool:
    """Whether there was such a web hook of the company; what it got goes with it."""
    query = delete(Webhook).where(Webhook.company_id == company_id, Webhook.id == webhook_id)

    async with Session() as session:
        result = await session.execute(query)
        await session.commit()

    return result.rowcount > 0


async def remove_company(company_id: uuid.UUID) -> None:
    async with Session() as session:
        await session.execute(delete(Webhook).where(Webhook.company_id == company_id))
        await session.commit()


async def of_user(user_id: str) -> list[Webhook]:
    async with Session() as session:
        return list(await session.scalars(select(Webhook).where(Webhook.created_by == user_id)))


async def remove_user(user_id: str) -> None:
    async with Session() as session:
        await session.execute(delete(Webhook).where(Webhook.created_by == user_id))
        await session.commit()


async def delivered(webhook_id: uuid.UUID, event_id: str) -> bool:
    query = select(WebhookDelivery).where(
        WebhookDelivery.webhook_id == webhook_id, WebhookDelivery.event_id == event_id
    )

    async with Session() as session:
        return await session.scalar(query) is not None


async def mark_delivered(webhook_id: uuid.UUID, event_id: str) -> None:
    """Notes the event as sent to the web hook, and forgets the web hook's ones long past
    redelivery (DELIVERIES_KEPT)."""
    old = delete(WebhookDelivery).where(
        WebhookDelivery.webhook_id == webhook_id,
        WebhookDelivery.delivered_at < datetime.now(UTC) - DELIVERIES_KEPT,
    )
    query = (
        insert(WebhookDelivery)
        .values(webhook_id=webhook_id, event_id=event_id)
        .on_conflict_do_nothing()
    )

    async with Session() as session:
        await session.execute(old)
        await session.execute(query)
        await session.commit()


async def set_failing(webhook_id: uuid.UUID, failing: bool) -> None:
    query = update(Webhook).where(Webhook.id == webhook_id).values(failing=failing)

    async with Session() as session:
        await session.execute(query)
        await session.commit()
