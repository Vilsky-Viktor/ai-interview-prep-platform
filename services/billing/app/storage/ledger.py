from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.credits import WELCOME_COMPANY, WELCOME_USER, GiftKind, HoldStatus, Reason
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


async def history(owner_type: str, owner_id: str, offset: int, limit: int) -> list[Entry]:
    """Every gift, top-up and charge, newest first."""
    query = (
        select(Entry)
        .where(Entry.owner_type == owner_type, Entry.owner_id == owner_id)
        .order_by(Entry.created_at.desc(), Entry.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def welcome(owner_type: str, owner_id: str, kind: str, email: str, amount: int) -> None:
    """Creates the wallet with the welcome gift, once per email and kind: a learner's first
    account, a person's first company. Deleting and signing up again doesn't repeat it."""
    async with Session() as session:
        await ensure(session, owner_type, owner_id)
        new = await session.scalar(
            insert(Gift)
            .values(key=gift_key(kind, email))
            .on_conflict_do_nothing()
            .returning(Gift.key)
        )

        if new:
            await add(session, owner_type, owner_id, amount, f"welcome:{owner_id}", Reason.WELCOME)

        await session.commit()


async def welcome_user(user_id: str, email: str) -> None:
    await welcome(OwnerType.USER, user_id, GiftKind.USER, email, WELCOME_USER)


async def welcome_company(company_id: str, owner_email: str) -> None:
    await welcome(OwnerType.COMPANY, company_id, GiftKind.COMPANY, owner_email, WELCOME_COMPANY)


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

        if hold is None:
            session.add(
                Hold(
                    key=key,
                    owner_type=owner_type,
                    owner_id=owner_id,
                    amount=amount,
                    reason=reason,
                    status=HoldStatus.OPEN,
                )
            )
        else:
            hold.status = HoldStatus.OPEN
            hold.amount = amount

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


async def spend(
    owner_type: str,
    owner_id: str,
    amount: int,
    key: str,
    reason: str,
    note: str | None = None,
    share: tuple[str, int] | None = None,
) -> bool:
    """Charges right away, for what is delivered at once (a chat turn, a certificate). Safe to
    repeat with the same key. `share` gives (user id, credits) of it to another learner, the
    author of a public kit, in the same transaction. False when the balance is too low."""
    async with Session() as session:
        if await session.scalar(select(Entry.id).where(Entry.key == key)):
            return True

        await ensure(session, owner_type, owner_id)
        row = await session.get(Wallet, (owner_type, owner_id), with_for_update=True)

        if row.balance - row.reserved < amount:
            await session.commit()

            return False

        await add(session, owner_type, owner_id, -amount, key, reason, note)

        if share:
            author_id, credits = share
            await ensure(session, OwnerType.USER, author_id)
            await add(
                session,
                OwnerType.USER,
                author_id,
                credits,
                f"{key}:share",
                Reason.AUTHOR_SHARE,
                note,
            )

        await session.commit()

        return True


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
    note: str | None = None,
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
            note=note,
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
