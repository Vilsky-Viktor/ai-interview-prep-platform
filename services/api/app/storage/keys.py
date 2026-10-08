import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, or_, select, update

from app.constants.api import LAST_USED_EVERY
from app.models.api import ApiKey
from app.storage.db import Session


async def of_company(company_id: uuid.UUID) -> list[ApiKey]:
    """Oldest first."""
    query = select(ApiKey).where(ApiKey.company_id == company_id).order_by(ApiKey.created_at)

    async with Session() as session:
        return list(await session.scalars(query))


async def count(company_id: uuid.UUID) -> int:
    query = select(func.count()).select_from(ApiKey).where(ApiKey.company_id == company_id)

    async with Session() as session:
        return await session.scalar(query) or 0


async def add(
    company_id: uuid.UUID,
    name: str,
    shown: str,
    hashed: str,
    user_id: str,
    expires_at: datetime | None,
) -> ApiKey:
    key = ApiKey(
        company_id=company_id,
        name=name,
        shown=shown,
        hash=hashed,
        created_by=user_id,
        expires_at=expires_at,
    )

    async with Session() as session:
        session.add(key)
        await session.commit()
        await session.refresh(key)

    return key


async def by_hash(hashed: str) -> ApiKey | None:
    async with Session() as session:
        return await session.scalar(select(ApiKey).where(ApiKey.hash == hashed))


async def used(key_id: uuid.UUID) -> None:
    """Notes the key was just used, at most once a minute (LAST_USED_EVERY)."""
    now = datetime.now(UTC)
    query = (
        update(ApiKey)
        .where(
            ApiKey.id == key_id,
            or_(ApiKey.last_used_at.is_(None), ApiKey.last_used_at < now - LAST_USED_EVERY),
        )
        .values(last_used_at=now)
    )

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def remove(company_id: uuid.UUID, key_id: uuid.UUID) -> bool:
    """Whether there was such a key of the company."""
    query = delete(ApiKey).where(ApiKey.company_id == company_id, ApiKey.id == key_id)

    async with Session() as session:
        result = await session.execute(query)
        await session.commit()

    return result.rowcount > 0


async def remove_company(company_id: uuid.UUID) -> None:
    async with Session() as session:
        await session.execute(delete(ApiKey).where(ApiKey.company_id == company_id))
        await session.commit()


async def of_user(user_id: str) -> list[ApiKey]:
    async with Session() as session:
        return list(await session.scalars(select(ApiKey).where(ApiKey.created_by == user_id)))


async def remove_user(user_id: str) -> None:
    async with Session() as session:
        await session.execute(delete(ApiKey).where(ApiKey.created_by == user_id))
        await session.commit()
