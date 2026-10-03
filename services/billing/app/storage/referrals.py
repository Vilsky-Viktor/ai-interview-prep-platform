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
from app.models.billing import Referral, Wallet
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
    """Notes that a new learner or company came through a link of its own kind. Not from
    yourself or a related company; the first link counts."""
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


async def reward(owner_type: str, owner_id: str) -> str | None:
    """Pays a referral once its new learner or company has topped up enough: both sides get
    the reward, the referrer only within their yearly limit and while their wallet exists.
    The referrer's id when it was paid."""
    amount = REFERRAL_REWARD[owner_type]
    now = datetime.now(UTC)

    async with Session() as session:
        referrer_id = await session.scalar(
            update(Referral)
            .where(
                Referral.owner_type == owner_type,
                Referral.owner_id == owner_id,
                Referral.rewarded_at.is_(None),
            )
            .values(rewarded_at=now)
            .returning(Referral.referrer_id)
        )

        if referrer_id is None:
            return None

        key = f"referral:{owner_type}:{owner_id}"
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


async def rewarded_count(owner_type: str, owner_id: str) -> int:
    """How many people or companies the owner brought in that have been rewarded."""
    async with Session() as session:
        return await session.scalar(
            select(func.count()).where(
                Referral.owner_type == owner_type,
                Referral.referrer_id == owner_id,
                Referral.rewarded_at.is_not(None),
            )
        )


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
