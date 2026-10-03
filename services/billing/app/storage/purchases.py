from datetime import datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.credits import Reason
from app.constants.products import DELETED_OWNER, OwnerType
from app.models.billing import Entry, Hold, Purchase, Wallet
from app.storage import referrals
from app.storage.db import Session
from app.storage.ledger import add, ensure


async def grant(
    owner_type: str,
    owner_id: str,
    credits: int,
    quantity: int,
    transaction_id: str,
    product: str,
    buyer_id: str | None,
    total: str,
    currency: str,
    now: datetime,
) -> bool:
    """Adds a paid top-up once per product of a transaction, however often Paddle retries.
    `credits` is what the whole line buys; `quantity` is kept for the accounts."""
    async with Session() as session:
        new = await session.scalar(
            insert(Purchase)
            .values(
                transaction_id=transaction_id,
                product=product,
                quantity=quantity,
                owner_type=owner_type,
                owner_id=owner_id,
                buyer_id=buyer_id,
                total=total,
                currency=currency,
                created_at=now,
            )
            .on_conflict_do_nothing()
            .returning(Purchase.id)
        )

        if new is None:
            await session.commit()

            return False

        await ensure(session, owner_type, owner_id)
        await add(
            session,
            owner_type,
            owner_id,
            credits,
            f"{transaction_id}:{product}",
            Reason.TOPUP,
        )
        await session.commit()

        return True


async def for_transaction(transaction_id: str) -> tuple[str, str, int, str] | None:
    """Whose wallet a transaction topped up, the credits it bought, and what was paid."""
    async with Session() as session:
        rows = list(
            await session.scalars(select(Purchase).where(Purchase.transaction_id == transaction_id))
        )

        if not rows:
            return None

        granted = await session.scalar(
            select(func.coalesce(func.sum(Entry.amount), 0)).where(
                Entry.key.in_([f"{transaction_id}:{row.product}" for row in rows])
            )
        )

    first = rows[0]

    return first.owner_type, first.owner_id, granted, first.total


async def purchases_of(user_id: str) -> list[Purchase]:
    query = (
        select(Purchase)
        .where(
            (Purchase.buyer_id == user_id)
            | ((Purchase.owner_type == OwnerType.USER) & (Purchase.owner_id == user_id))
        )
        .order_by(Purchase.created_at)
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def delete_user(user_id: str) -> None:
    """The learner's wallet, holds and history go; purchases stay for the accounts, without
    them."""
    is_user = {"owner_type": OwnerType.USER, "owner_id": user_id}

    async with Session() as session:
        await session.execute(delete(Wallet).filter_by(**is_user))
        await session.execute(delete(Hold).filter_by(**is_user))
        await session.execute(delete(Entry).filter_by(**is_user))
        await referrals.forget(session, OwnerType.USER, user_id)
        await session.execute(update(Purchase).filter_by(**is_user).values(owner_id=DELETED_OWNER))
        await session.execute(
            update(Purchase).where(Purchase.buyer_id == user_id).values(buyer_id=None)
        )
        await session.commit()


async def delete_company(company_id: str) -> None:
    """A deleted company's wallet, holds and history; its purchases stay for the accounts."""
    is_company = {"owner_type": OwnerType.COMPANY, "owner_id": company_id}

    async with Session() as session:
        await session.execute(delete(Wallet).filter_by(**is_company))
        await session.execute(delete(Hold).filter_by(**is_company))
        await session.execute(delete(Entry).filter_by(**is_company))
        await referrals.forget(session, OwnerType.COMPANY, company_id)
        await session.commit()
