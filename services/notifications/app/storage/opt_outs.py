from sqlalchemy import delete, exists, or_, select
from sqlalchemy.dialects.postgresql import insert

from app.models.opt_outs import CandidateOptOut
from app.storage.db import Session


async def add(address: str, company_id: str, invite_id: str | None = None) -> None:
    """Stops the company's emails to the address (its hash), or with `invite_id` only that
    invite's reminders. Safe to repeat."""
    async with Session() as session:
        await session.execute(
            insert(CandidateOptOut)
            .values(address=address, company_id=company_id, invite_id=invite_id)
            .on_conflict_do_nothing()
        )
        await session.commit()


async def opted_out(address: str, company_id: str, invite_id: str | None = None) -> bool:
    """Whether the address (its hash) stopped the company's emails, or (given an invite) its
    reminders."""
    query = select(
        exists().where(
            CandidateOptOut.address == address,
            CandidateOptOut.company_id == company_id,
            or_(CandidateOptOut.invite_id.is_(None), CandidateOptOut.invite_id == invite_id),
        )
    )

    async with Session() as session:
        return bool(await session.scalar(query))


async def of_address(address: str) -> list[CandidateOptOut]:
    """Every opt-out of the address (its hash): from a company's emails, or an invite's
    reminders."""
    query = select(CandidateOptOut).where(CandidateOptOut.address == address)

    async with Session() as session:
        return list(await session.scalars(query))


async def remove(address: str, company_id: str) -> None:
    """The address (its hash) hears from the company again: its opt-out from all the company's
    emails and from any invite's reminders go. Safe to repeat."""
    async with Session() as session:
        await session.execute(
            delete(CandidateOptOut).where(
                CandidateOptOut.address == address, CandidateOptOut.company_id == company_id
            )
        )
        await session.commit()


async def remove_company(company_id: str) -> None:
    """A deleted company emails nobody again: its candidates' wishes go with it."""
    async with Session() as session:
        await session.execute(
            delete(CandidateOptOut).where(CandidateOptOut.company_id == company_id)
        )
        await session.commit()
