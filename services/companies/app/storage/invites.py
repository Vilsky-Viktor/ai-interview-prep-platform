import secrets
import uuid
from datetime import UTC, datetime

from prepza_common import outbox
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.events import CANDIDATE_INVITED
from app.constants.invites import InviteStatus
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.models.outbox import OutboxEvent
from app.storage.db import Session


async def upsert(interview_id, email: str, title: str, company: str) -> CandidateInvite:
    """Creates the invite, or returns the existing one so it can be sent again, and saves the
    email's event with it."""
    email = email.lower()
    statement = (
        insert(CandidateInvite)
        .values(
            id=uuid.uuid4(),
            interview_id=interview_id,
            email=email,
            token=secrets.token_urlsafe(32),
            status=InviteStatus.INVITED,
            created_at=datetime.now(UTC),
        )
        .on_conflict_do_nothing(index_elements=["interview_id", "email"])
    )

    async with Session() as session:
        await session.execute(statement)
        invite = await session.scalar(
            select(CandidateInvite).where(
                CandidateInvite.interview_id == interview_id, CandidateInvite.email == email
            )
        )

        if invite.status == InviteStatus.UNDELIVERED:
            invite.status = InviteStatus.INVITED

        outbox.add(
            session,
            OutboxEvent,
            CANDIDATE_INVITED,
            {
                "invite_id": str(invite.id),
                "email": invite.email,
                "token": invite.token,
                "title": title,
                "company": company,
            },
        )
        await session.commit()

        return invite


async def exists(interview_id, email: str) -> bool:
    query = select(CandidateInvite.id).where(
        CandidateInvite.interview_id == interview_id, CandidateInvite.email == email.lower()
    )

    async with Session() as session:
        return await session.scalar(query) is not None


async def get_by_token(token: str) -> tuple[CandidateInvite, Interview] | None:
    query = (
        select(CandidateInvite, Interview)
        .join(Interview, Interview.id == CandidateInvite.interview_id)
        .where(CandidateInvite.token == token)
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

        return tuple(row) if row else None


async def start(invite: CandidateInvite, user_id: str) -> None:
    async with Session() as session:
        stored = await session.get(CandidateInvite, invite.id)
        stored.user_id = user_id

        if stored.status in (InviteStatus.INVITED, InviteStatus.UNDELIVERED):
            stored.status = InviteStatus.IN_PROCESS

        await session.commit()


async def mark_undelivered(invite_id: uuid.UUID) -> None:
    """Only an unused invite: a candidate who has started got the email after all."""
    async with Session() as session:
        await session.execute(
            update(CandidateInvite)
            .where(
                CandidateInvite.id == invite_id,
                CandidateInvite.status == InviteStatus.INVITED,
            )
            .values(status=InviteStatus.UNDELIVERED)
        )
        await session.commit()


async def set_status(invite_ids: list, status: str) -> None:
    if not invite_ids:
        return

    async with Session() as session:
        await session.execute(
            update(CandidateInvite).where(CandidateInvite.id.in_(invite_ids)).values(status=status)
        )
        await session.commit()


async def remove(invite_id: uuid.UUID) -> None:
    """Deletes the invite; its link stops working."""
    async with Session() as session:
        await session.execute(delete(CandidateInvite).where(CandidateInvite.id == invite_id))
        await session.commit()


async def list_for_interview(interview_id, offset: int, limit: int) -> list[CandidateInvite]:
    query = (
        select(CandidateInvite)
        .where(CandidateInvite.interview_id == interview_id)
        .order_by(CandidateInvite.created_at.desc(), CandidateInvite.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))
