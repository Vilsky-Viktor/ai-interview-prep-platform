import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.credits import (
    REFERRAL_CODE_BYTES,
    REFERRAL_REWARD,
    REFERRALS_PER_YEAR,
    Reason,
)
from app.constants.products import DELETED_OWNER
from app.models.billing import Entry, Referral, Wallet
from app.storage.db import Session
from app.storage.ledger import add, ensure


async def code_of(owner_type: str, owner_id: str) -> str:
    """The owner's referral code, made the first time it's asked for."""
    async with Session() as session:
        await ensure(session, owner_type, owner_id)
        row = await session.get(Wallet, (owner_type, owner_id), with_for_update=True)

        if row.referral_code is None:
            row.referral_code = secrets.token_urlsafe(REFERRAL_CODE_BYTES)

        await session.commit()

        return row.referral_code


async def record(code: str, owner_type: str, owner_id: str, related: list[str]) -> bool:
    """Notes that a new company came through another company's link. Not from itself or a
    related company; the first link counts."""
    async with Session() as session:
        referrer_id = await session.scalar(
            select(Wallet.owner_id).where(
                Wallet.referral_code == code, Wallet.owner_type == owner_type
            )
        )

        if referrer_id is None or referrer_id == owner_id or referrer_id in related:
            return False

        new = await session.scalar(
            insert(Referral)
            .values(owner_type=owner_type, owner_id=owner_id, referrer_id=referrer_id)
            .on_conflict_do_nothing()
            .returning(Referral.owner_id)
        )
        await session.commit()

        return new is not None


def reward_key(owner_type: str, owner_id: str, transaction_id: str) -> str:
    return f"referral:{owner_type}:{owner_id}:{transaction_id}"


async def reward(owner_type: str, owner_id: str, transaction_id: str) -> str | None:
    """Pays a referral once its new company has topped up (`transaction_id`): both sides get
    the reward, the referrer only within their yearly limit and while their wallet exists.
    The referrer's id when it was paid."""
    amount = REFERRAL_REWARD
    now = datetime.now(UTC)
    key = reward_key(owner_type, owner_id, transaction_id)

    async with Session() as session:
        # A top-up pays at most once: a redelivery after its reward was taken back (refund)
        # leaves the referral for the next real top-up.
        if await session.scalar(select(Entry.key).where(Entry.key == key)):
            return None

        referrer_id = await session.scalar(
            update(Referral)
            .where(
                Referral.owner_type == owner_type,
                Referral.owner_id == owner_id,
                Referral.rewarded_at.is_(None),
            )
            .values(rewarded_at=now, rewarded_by=transaction_id)
            .returning(Referral.referrer_id)
        )

        if referrer_id is None:
            return None

        await add(session, owner_type, owner_id, amount, key, Reason.REFERRAL)
        rewarded_this_year = await session.scalar(
            select(func.count()).where(
                Referral.owner_type == owner_type,
                Referral.referrer_id == referrer_id,
                Referral.rewarded_at > now - timedelta(days=365),
            )
        )
        referrer = await session.get(Wallet, (owner_type, referrer_id))

        # This one is already counted, hence <=.
        if referrer is not None and rewarded_this_year <= REFERRALS_PER_YEAR:
            await add(session, owner_type, referrer_id, amount, f"{key}:referrer", Reason.REFERRAL)

        await session.commit()

        return referrer_id


async def take_back(transaction_id: str) -> bool:
    """The top-up that paid a referral was refunded in full or charged back: both sides' rewards
    go back (from wallets that still exist), and the referral waits for the company's next
    top-up. Once per transaction, however often Paddle sends the adjustment. True when there
    was a reward to take back."""
    async with Session() as session:
        referral = await session.scalar(
            update(Referral)
            .where(Referral.rewarded_by == transaction_id)
            .values(rewarded_at=None, rewarded_by=None)
            .returning(Referral)
        )

        if referral is None:
            return False

        key = reward_key(referral.owner_type, referral.owner_id, transaction_id)
        paid = await session.scalars(select(Entry).where(Entry.key.in_([key, f"{key}:referrer"])))

        for entry in list(paid):
            await add(
                session,
                entry.owner_type,
                entry.owner_id,
                -entry.amount,
                f"{entry.key}:reversed",
                Reason.REFERRAL_REVERSED,
            )

        await session.commit()

        return True


async def rewarded_count(owner_type: str, owner_id: str) -> int:
    """How many companies the owner brought in that have been rewarded."""
    async with Session() as session:
        return await session.scalar(
            select(func.count()).where(
                Referral.owner_type == owner_type,
                Referral.referrer_id == owner_id,
                Referral.rewarded_at.is_not(None),
            )
        )


async def rewards(owner_type: str, owner_id: str, limit: int) -> list[Referral]:
    """The companies the owner brought in that have been rewarded, newest first."""
    query = (
        select(Referral)
        .where(
            Referral.owner_type == owner_type,
            Referral.referrer_id == owner_id,
            Referral.rewarded_at.is_not(None),
        )
        .order_by(Referral.rewarded_at.desc())
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def forget(session: AsyncSession, owner_type: str, owner_id: str) -> None:
    """On deletion: the owner's own referral goes. The ones they made lose their name, so the
    people they brought in still get their own reward."""
    is_owner = {"owner_type": owner_type}
    await session.execute(delete(Referral).filter_by(**is_owner, owner_id=owner_id))
    await session.execute(
        update(Referral)
        .filter_by(**is_owner, referrer_id=owner_id)
        .values(referrer_id=DELETED_OWNER)
    )
