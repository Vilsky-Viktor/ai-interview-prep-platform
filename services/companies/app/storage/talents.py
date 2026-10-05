from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.models.talents import HiddenTalent
from app.storage.db import Session


async def hidden_urls(interview_id) -> set[str]:
    async with Session() as session:
        rows = await session.scalars(
            select(HiddenTalent.url).where(HiddenTalent.interview_id == interview_id)
        )

        return set(rows)


async def hide(interview_id, url: str) -> None:
    async with Session() as session:
        await session.execute(
            insert(HiddenTalent).values(interview_id=interview_id, url=url).on_conflict_do_nothing()
        )
        await session.commit()
