from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.models.legal_notices import LegalNotice
from app.storage.db import Session


async def all_notices() -> list[LegalNotice]:
    async with Session() as session:
        return list(await session.scalars(select(LegalNotice)))


async def ask(document: str, version: str, user_id: str) -> bool:
    """False when this version's notice was asked for already (two clicks at once too)."""
    async with Session() as session:
        added = await session.scalar(
            insert(LegalNotice)
            .values(document=document, version=version, asked_by=user_id)
            .on_conflict_do_nothing()
            .returning(LegalNotice.document)
        )
        await session.commit()

    return added is not None


async def sent(document: str, version: str) -> None:
    async with Session() as session:
        await session.execute(
            update(LegalNotice)
            .where(LegalNotice.document == document, LegalNotice.version == version)
            .values(sent_at=datetime.now(UTC))
        )
        await session.commit()
