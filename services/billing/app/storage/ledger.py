from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.credits import WELCOME_COMPANY, WELCOME_GIFT, HoldStatus, Reason
from app.constants.products import OwnerType
from app.helpers.gifts import gift_key
from app.models.billing import Entry, Gift, Hold, Wallet
from app.storage.db import Session


async def wallet(owner_type: str, owner_id: str) -> Wallet:
    """The wallet, created empty the first time."""
    async with Session() as session:
        await ensure(session, owner_type, owner_id)
        await session.commit()

        return await session.get(Wallet, (owner_type, owner_id))


async def wallets(owner_type: str, owner_ids: list[str]) -> dict[str, Wallet]:
    """Existing wallets by owner id; owners without one have nothing yet."""
    query = select(Wallet).where(Wallet.owner_type == owner_type, Wallet.owner_id.in_(owner_ids))

    async with Session() as session:
        return {row.owner_id: row for row in await session.scalars(query)}


async def welcome_company(company_id: str, owner_email: str) -> bool:
    """Creates the company's wallet with the welcome credits, once per owner's email: a person's
    first company. Deleting and creating one again doesn't repeat it. True when the gift is new."""
    async with Session() as session:
        await ensure(session, OwnerType.COMPANY, company_id)
        new = await session.scalar(
            insert(Gift)
            .values(key=gift_key(WELCOME_GIFT, owner_email))
            .on_conflict_do_nothing()
            .returning(Gift.key)
        )

        if new:
            await add(
                session,
                OwnerType.COMPANY,
                company_id,
                WELCOME_COMPANY,
                f"welcome:{company_id}",
                Reason.WELCOME,
            )

        await session.commit()

        return bool(new)


async def reserve(owner_type: str, owner_id: str, amount: int, key: str, reason: str) -> bool:
    """Sets credits aside. Repeating the same key does it once; a released hold can be taken
    again. False when the available balance is too low."""
    async with Session() as session:
        await ensure(session, owner_type, owner_id)
        # The wallet's lock comes first, so two requests for the same hold can't both add it.
        row = await session.get(Wallet, (owner_type, owner_id), with_for_update=True)
        hold = await session.get(Hold, key)

        if hold is not None and hold.status != HoldStatus.RELEASED:
            await session.commit()

            return True

        if row.balance - row.reserved < amount:
            await session.commit()

            return False

        row.reserved += amount
        # A new hold, or the released one with this key opened again.
        await session.merge(
            Hold(
                key=key,
                owner_type=owner_type,
                owner_id=owner_id,
                amount=amount,
                reason=reason,
                status=HoldStatus.OPEN,
            )
        )
        await session.commit()

        return True


async def charge(key: str) -> None:
    """Takes the credits a hold set aside. Safe to repeat; does nothing without an open hold."""
    async with Session() as session:
        hold = await session.get(Hold, key, with_for_update=True)

        if hold is None or hold.status != HoldStatus.OPEN:
            return

        await session.execute(
            update(Wallet)
            .where(Wallet.owner_type == hold.owner_type, Wallet.owner_id == hold.owner_id)
            .values(reserved=Wallet.reserved - hold.amount)
        )
        await add(session, hold.owner_type, hold.owner_id, -hold.amount, key, hold.reason)
        hold.status = HoldStatus.CHARGED
        await session.commit()


async def release(key: str) -> None:
    """Gives back credits a hold set aside. Safe to repeat."""
    async with Session() as session:
        hold = await session.get(Hold, key, with_for_update=True)

        if hold is None or hold.status != HoldStatus.OPEN:
            return

        await session.execute(
            update(Wallet)
            .where(Wallet.owner_type == hold.owner_type, Wallet.owner_id == hold.owner_id)
            .values(reserved=Wallet.reserved - hold.amount)
        )
        hold.status = HoldStatus.RELEASED
        await session.commit()


async def adjust(owner_type: str, owner_id: str, amount: int, key: str, reason: str) -> None:
    """Moves credits whatever the balance: a refund or chargeback may leave it negative."""
    async with Session() as session:
        await ensure(session, owner_type, owner_id)
        await add(session, owner_type, owner_id, amount, key, reason)
        await session.commit()


async def ensure(session: AsyncSession, owner_type: str, owner_id: str) -> None:
    """Creates the wallet, empty; the welcome gift comes from welcome()."""
    await session.execute(
        insert(Wallet)
        .values(owner_type=owner_type, owner_id=owner_id, balance=0, reserved=0)
        .on_conflict_do_nothing()
    )


async def add(
    session: AsyncSession,
    owner_type: str,
    owner_id: str,
    amount: int,
    key: str,
    reason: str,
) -> bool:
    """Records one movement and applies it to the balance, once per key."""
    new = await session.scalar(
        insert(Entry)
        .values(
            key=key,
            owner_type=owner_type,
            owner_id=owner_id,
            amount=amount,
            reason=reason,
        )
        .on_conflict_do_nothing()
        .returning(Entry.id)
    )

    if new is None:
        return False

    await session.execute(
        update(Wallet)
        .where(Wallet.owner_type == owner_type, Wallet.owner_id == owner_id)
        .values(balance=Wallet.balance + amount)
    )

    return True
