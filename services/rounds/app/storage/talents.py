from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from app.models.sessions import Session as SessionRow
from app.models.talents import TalentLink
from app.storage.db import Session


async def get(user_id: str) -> TalentLink | None:
    async with Session() as session:
        return await session.get(TalentLink, user_id)


async def save(user_id: str, name: str, url: str | None) -> TalentLink:
    """Saves the talent's answer: their link to be suggested, or none when they decline or
    withdraw; answering again replaces it."""
    now = datetime.now(UTC)
    statement = (
        insert(TalentLink)
        .values(user_id=user_id, name=name, url=url, decided_at=now)
        .on_conflict_do_update(
            index_elements=["user_id"], set_={"name": name, "url": url, "decided_at": now}
        )
        .returning(TalentLink)
    )

    async with Session() as session:
        saved = await session.scalar(statement)
        await session.commit()

        return saved


async def practice_of_consenting(template_ids: list) -> tuple[list[Session], dict]:
    """Practice sections on the templates by talents who agreed to be suggested, with their
    links by user."""
    async with Session() as session:
        links = {
            link.user_id: link
            for link in await session.scalars(select(TalentLink).where(TalentLink.url.is_not(None)))
        }
        rows = (
            list(
                await session.scalars(
                    select(SessionRow)
                    .where(
                        SessionRow.practice.is_(True),
                        SessionRow.interview_set_id.in_(template_ids),
                        SessionRow.user_id.in_(list(links)),
                    )
                    .options(selectinload(SessionRow.answers))
                )
            )
            if links
            else []
        )

    return rows, links
