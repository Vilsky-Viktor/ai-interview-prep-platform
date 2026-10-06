from datetime import datetime

from sqlalchemy import case, delete, or_, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.products import AUTO_TOP_UP_COOLDOWN, AUTO_TOP_UP_RETRY_AFTER
from app.models.billing import AutoTopUp, Wallet
from app.storage.db import Session


async def get(owner_type: str, owner_id: str) -> AutoTopUp | None:
    async with Session() as session:
        return await session.get(AutoTopUp, (owner_type, owner_id))


async def save(
    owner_type: str, owner_id: str, product: str, threshold: int, buyer_id: str
) -> AutoTopUp:
    """Sets what to buy and when, and allows a declined charge to be tried again at once. A
    running one keeps its subscription and the card it charges; one still waiting for its
    checkout waits for this person's, whoever turned it on before."""
    values = {"product": product, "threshold": threshold}
    upsert = insert(AutoTopUp).values(
        owner_type=owner_type, owner_id=owner_id, buyer_id=buyer_id, **values
    )
    waiting = AutoTopUp.subscription_id.is_(None)

    async with Session() as session:
        await session.execute(
            upsert.on_conflict_do_update(
                index_elements=["owner_type", "owner_id"],
                set_={
                    **values,
                    "buyer_id": case((waiting, upsert.excluded.buyer_id), else_=AutoTopUp.buyer_id),
                    "failed_at": None,
                },
            )
        )
        await session.commit()

        return await session.get(AutoTopUp, (owner_type, owner_id))


async def start(owner_type: str, owner_id: str, buyer_id: str, subscription_id: str) -> bool:
    """Attaches the subscription from the checkout of whoever turned it on; once only. Paddle's
    two events for one checkout can arrive together, so finding it already attached counts as
    started too."""
    async with Session() as session:
        started = await session.scalar(
            update(AutoTopUp)
            .where(
                AutoTopUp.owner_type == owner_type,
                AutoTopUp.owner_id == owner_id,
                AutoTopUp.buyer_id == buyer_id,
                or_(
                    AutoTopUp.subscription_id.is_(None),
                    AutoTopUp.subscription_id == subscription_id,
                ),
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
    """The running automatic top-up, if the available balance is under its threshold, it
    hasn't charged within the cooldown and the card hasn't declined within the retry wait;
    marks it charged now. Atomic, so two requests at once charge once."""
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
            or_(
                AutoTopUp.failed_at.is_(None),
                AutoTopUp.failed_at < now - AUTO_TOP_UP_RETRY_AFTER,
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


async def failed(owner_type: str, owner_id: str, now: datetime) -> None:
    """The card declined the charge: the next try waits (claim_charge)."""
    async with Session() as session:
        await session.execute(
            update(AutoTopUp)
            .where(AutoTopUp.owner_type == owner_type, AutoTopUp.owner_id == owner_id)
            .values(failed_at=now)
        )
        await session.commit()


async def remove(owner_type: str, owner_id: str, buyer_id: str | None = None) -> str | None:
    """Turns it off, or only when `buyer_id` turned it on; the subscription to cancel, if it had
    started."""
    query = delete(AutoTopUp).where(
        AutoTopUp.owner_type == owner_type, AutoTopUp.owner_id == owner_id
    )

    if buyer_id is not None:
        query = query.where(AutoTopUp.buyer_id == buyer_id)

    async with Session() as session:
        subscription_id = await session.scalar(query.returning(AutoTopUp.subscription_id))
        await session.commit()

        return subscription_id


async def remove_for_buyer(buyer_id: str) -> list[str]:
    """Turns off every automatic top-up paid with this person's card; the subscriptions to
    cancel."""
    async with Session() as session:
        rows = await session.scalars(
            delete(AutoTopUp)
            .where(AutoTopUp.buyer_id == buyer_id)
            .returning(AutoTopUp.subscription_id)
        )
        subscriptions = [row for row in rows if row]
        await session.commit()

        return subscriptions


async def remove_subscription(subscription_id: str) -> None:
    """Paddle ended the subscription: automatic top-up is off."""
    async with Session() as session:
        await session.execute(delete(AutoTopUp).where(AutoTopUp.subscription_id == subscription_id))
        await session.commit()
