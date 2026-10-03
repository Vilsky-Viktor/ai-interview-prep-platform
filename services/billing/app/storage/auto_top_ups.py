from datetime import datetime

from sqlalchemy import delete, or_, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.products import AUTO_TOP_UP_COOLDOWN
from app.models.billing import AutoTopUp, Wallet
from app.storage.db import Session


async def get(owner_type: str, owner_id: str) -> AutoTopUp | None:
    async with Session() as session:
        return await session.get(AutoTopUp, (owner_type, owner_id))


async def save(
    owner_type: str, owner_id: str, product: str, threshold: int, buyer_id: str
) -> AutoTopUp:
    """Sets what to buy and when. A running one keeps its subscription; a new one waits for
    its checkout."""
    values = {"product": product, "threshold": threshold}

    async with Session() as session:
        await session.execute(
            insert(AutoTopUp)
            .values(owner_type=owner_type, owner_id=owner_id, buyer_id=buyer_id, **values)
            .on_conflict_do_update(index_elements=["owner_type", "owner_id"], set_=values)
        )
        await session.commit()

        return await session.get(AutoTopUp, (owner_type, owner_id))


async def start(owner_type: str, owner_id: str, buyer_id: str, subscription_id: str) -> bool:
    """Attaches the subscription from the checkout of whoever turned it on; once only."""
    async with Session() as session:
        started = await session.scalar(
            update(AutoTopUp)
            .where(
                AutoTopUp.owner_type == owner_type,
                AutoTopUp.owner_id == owner_id,
                AutoTopUp.buyer_id == buyer_id,
                AutoTopUp.subscription_id.is_(None),
            )
            .values(subscription_id=subscription_id)
            .returning(AutoTopUp.owner_id)
        )
        await session.commit()

        return started is not None


async def owner_of(subscription_id: str) -> tuple[str, str] | None:
    """Whose wallet an automatic charge is for."""
    query = select(AutoTopUp.owner_type, AutoTopUp.owner_id).where(
        AutoTopUp.subscription_id == subscription_id
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

    return (row.owner_type, row.owner_id) if row else None


async def claim_charge(owner_type: str, owner_id: str, now: datetime) -> AutoTopUp | None:
    """The running automatic top-up, if the available balance is under its threshold and it
    hasn't charged within the cooldown; marks it charged now. Atomic, so two requests at once
    charge once."""
    query = (
        update(AutoTopUp)
        .where(
            AutoTopUp.owner_type == owner_type,
            AutoTopUp.owner_id == owner_id,
            AutoTopUp.subscription_id.is_not(None),
            or_(
                AutoTopUp.charged_at.is_(None),
                AutoTopUp.charged_at < now - AUTO_TOP_UP_COOLDOWN,
            ),
            Wallet.owner_type == AutoTopUp.owner_type,
            Wallet.owner_id == AutoTopUp.owner_id,
            Wallet.balance - Wallet.reserved < AutoTopUp.threshold,
        )
        .values(charged_at=now)
        .returning(AutoTopUp)
    )

    async with Session() as session:
        row = await session.scalar(query)
        await session.commit()

        return row


async def remove(owner_type: str, owner_id: str) -> str | None:
    """Turns it off; the subscription to cancel, if it had started."""
    async with Session() as session:
        subscription_id = await session.scalar(
            delete(AutoTopUp)
            .where(AutoTopUp.owner_type == owner_type, AutoTopUp.owner_id == owner_id)
            .returning(AutoTopUp.subscription_id)
        )
        await session.commit()

        return subscription_id


async def remove_subscription(subscription_id: str) -> None:
    """Paddle ended the subscription: automatic top-up is off."""
    async with Session() as session:
        await session.execute(delete(AutoTopUp).where(AutoTopUp.subscription_id == subscription_id))
        await session.commit()
