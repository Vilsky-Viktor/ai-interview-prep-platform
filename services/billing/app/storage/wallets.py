from datetime import date, datetime, timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.products import (
    DELETED_OWNER,
    FREE_CANDIDATES,
    FREE_GENERATIONS_PER_MONTH,
    OwnerType,
    Product,
)
from app.models.billing import MonthlyUsage, Purchase, Wallet
from app.storage.db import Session


def first_of_month(now: datetime) -> date:
    return date(now.year, now.month, 1)


async def get(owner_type: str, owner_id: str) -> Wallet | None:
    async with Session() as session:
        return await session.get(Wallet, (owner_type, owner_id))


async def ensure_company(session, company_id: str) -> None:
    """A company's wallet starts with its free candidates."""
    await session.execute(
        insert(Wallet)
        .values(
            owner_type=OwnerType.COMPANY,
            owner_id=company_id,
            candidate_credits=FREE_CANDIDATES,
            generation_credits=0,
        )
        .on_conflict_do_nothing()
    )


async def company_credits(company_id: str) -> int:
    async with Session() as session:
        await ensure_company(session, company_id)
        await session.commit()

        return await session.scalar(
            select(Wallet.candidate_credits).where(
                Wallet.owner_type == OwnerType.COMPANY, Wallet.owner_id == company_id
            )
        )


async def use_candidate(company_id: str) -> bool:
    """Takes one candidate credit; False when none is left."""
    async with Session() as session:
        await ensure_company(session, company_id)
        used = await session.scalar(
            update(Wallet)
            .where(
                Wallet.owner_type == OwnerType.COMPANY,
                Wallet.owner_id == company_id,
                Wallet.candidate_credits > 0,
            )
            .values(candidate_credits=Wallet.candidate_credits - 1)
            .returning(Wallet.owner_id)
        )
        await session.commit()

        return used is not None


async def free_generations_used(user_id: str, now: datetime) -> int:
    async with Session() as session:
        used = await session.scalar(
            select(MonthlyUsage.free_generations).where(
                MonthlyUsage.user_id == user_id, MonthlyUsage.month == first_of_month(now)
            )
        )

        return used or 0


async def use_generation(user_id: str, now: datetime) -> bool:
    """A pass covers it; otherwise the month's free one, then a bought credit. False when
    nothing is left."""
    async with Session() as session:
        wallet = await session.get(Wallet, (OwnerType.USER, user_id))

        if wallet and wallet.pass_until and wallet.pass_until > now:
            return True

        free = await session.scalar(
            insert(MonthlyUsage)
            .values(user_id=user_id, month=first_of_month(now), free_generations=1)
            .on_conflict_do_update(
                index_elements=["user_id", "month"],
                set_={"free_generations": MonthlyUsage.free_generations + 1},
                where=MonthlyUsage.free_generations < FREE_GENERATIONS_PER_MONTH,
            )
            .returning(MonthlyUsage.user_id)
        )

        if free is None:
            free = await session.scalar(
                update(Wallet)
                .where(
                    Wallet.owner_type == OwnerType.USER,
                    Wallet.owner_id == user_id,
                    Wallet.generation_credits > 0,
                )
                .values(generation_credits=Wallet.generation_credits - 1)
                .returning(Wallet.owner_id)
            )

        await session.commit()

        return free is not None


async def grant(
    transaction_id: str,
    lines: list[tuple[Product, int]],
    owner_id: str,
    buyer_id: str | None,
    total: str,
    currency: str,
    now: datetime,
) -> int:
    """Records a paid transaction and adds what it bought, once per product however often
    Paddle retries. Returns how many lines were new."""
    added = 0

    async with Session() as session:
        for product, quantity in lines:
            new = await session.scalar(
                insert(Purchase)
                .values(
                    transaction_id=transaction_id,
                    product=product.key,
                    quantity=quantity,
                    owner_type=product.owner,
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
                continue

            added += 1

            if product.owner == OwnerType.COMPANY:
                await ensure_company(session, owner_id)

            await session.execute(
                insert(Wallet)
                .values(
                    owner_type=product.owner,
                    owner_id=owner_id,
                    candidate_credits=0,
                    generation_credits=0,
                )
                .on_conflict_do_nothing()
            )
            wallet = await session.get(Wallet, (product.owner, owner_id), with_for_update=True)
            wallet.candidate_credits += product.candidate_credits * quantity
            wallet.generation_credits += product.generation_credits * quantity

            if product.pass_days:
                start = max(wallet.pass_until or now, now)
                wallet.pass_until = start + timedelta(days=product.pass_days * quantity)

        await session.commit()

    return added


async def delete_user(user_id: str) -> None:
    """The user's wallet and usage go; their purchases stay for bookkeeping, without them."""
    async with Session() as session:
        await session.execute(
            delete(Wallet).where(Wallet.owner_type == OwnerType.USER, Wallet.owner_id == user_id)
        )
        await session.execute(delete(MonthlyUsage).where(MonthlyUsage.user_id == user_id))
        await session.execute(
            update(Purchase)
            .where(Purchase.owner_type == OwnerType.USER, Purchase.owner_id == user_id)
            .values(owner_id=DELETED_OWNER)
        )
        await session.execute(
            update(Purchase).where(Purchase.buyer_id == user_id).values(buyer_id=None)
        )
        await session.commit()


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
