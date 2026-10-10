import secrets

from prepza_common import outbox
from prepza_common.notifications import NOTIFICATION_REQUESTED
from sqlalchemy import delete, select, update

from app.constants.events import MEMBER_INVITED
from app.constants.roles import Role
from app.helpers.notifications import member_joined
from app.models.companies import Company, Member
from app.models.outbox import OutboxEvent
from app.storage.db import Session


async def add(company_id, email: str, role: str, sender: dict) -> Member:
    """A pending invite; the role applies once it's accepted. Its email's event is saved with it:
    `sender` (the company, its logo, the inviter and their language) and the join link's token."""
    member = Member(
        company_id=company_id,
        invited_email=email.lower(),
        role=role,
        token=secrets.token_urlsafe(32),
    )

    async with Session() as session:
        session.add(member)
        outbox.add(
            session,
            OutboxEvent,
            MEMBER_INVITED,
            {**sender, "email": member.invited_email, "token": member.token, "role": role},
        )
        await session.commit()

    return member


async def get_by_token(token: str) -> tuple[Member, Company] | None:
    query = (
        select(Member, Company)
        .join(Company, Company.id == Member.company_id)
        .where(Member.token == token)
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

        return tuple(row) if row else None


async def accept(member: Member, company: Company, user_id: str) -> None:
    """Joins the member, and tells the owner in the bell, in the same transaction."""
    async with Session() as session:
        row = await session.get(Member, member.id)
        joining = row.user_id is None

        if joining:
            row.user_id = user_id

        # The link works once: a joined member no longer needs it.
        row.token = None

        owner_id = await session.scalar(
            select(Member.user_id).where(Member.company_id == company.id, Member.role == Role.OWNER)
        )

        if joining and owner_id:
            outbox.add(
                session, OutboxEvent, NOTIFICATION_REQUESTED, member_joined(company, row, owner_id)
            )

        await session.commit()


async def list_for_company(company_id, offset: int, limit: int) -> list[Member]:
    query = (
        select(Member)
        .where(Member.company_id == company_id)
        .order_by(Member.created_at, Member.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def set_role(member_id, role: str) -> None:
    async with Session() as session:
        await session.execute(update(Member).where(Member.id == member_id).values(role=role))
        await session.commit()


async def remove(member_id) -> None:
    async with Session() as session:
        await session.execute(delete(Member).where(Member.id == member_id))
        await session.commit()
