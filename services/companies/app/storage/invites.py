import secrets
import uuid
from datetime import UTC, datetime

from prepza_common import outbox
from prepza_common.notifications import NOTIFICATION_REQUESTED
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.events import CANDIDATE_INVITED
from app.constants.invites import NOT_STARTED, InviteStatus
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.models.outbox import OutboxEvent
from app.storage.db import Session


async def upsert(
    interview_id, email: str, title: str, company: str, language: str, logo_path: str | None = None
) -> CandidateInvite:
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
            sent_at=datetime.now(UTC),
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

        # Sending again revives an undelivered or expired invite and restarts its 30 days.
        if invite.status in (InviteStatus.UNDELIVERED, InviteStatus.EXPIRED):
            invite.status = InviteStatus.INVITED

        invite.sent_at = datetime.now(UTC)
        invite.reminded_at = None

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
                "language": language,
                # The company's logo for the top of the email, when it has one.
                "logo_path": logo_path,
            },
        )
        await session.commit()

        return invite


async def for_link(interview_id, email: str) -> CandidateInvite:
    """The candidate who came through the test's link: their invite, made now if it's new. No
    email goes out: they're already here."""
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
            sent_at=datetime.now(UTC),
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
        await session.commit()

        return invite


async def status_of(interview_id, email: str) -> str | None:
    """The invite's status, or None when this email hasn't been invited."""
    query = select(CandidateInvite.status).where(
        CandidateInvite.interview_id == interview_id, CandidateInvite.email == email.lower()
    )

    async with Session() as session:
        return await session.scalar(query)


async def unfinished(interview_id) -> list[tuple]:
    """(interview id, email, status) of the interview's invites not finished yet."""
    query = select(
        CandidateInvite.interview_id, CandidateInvite.email, CandidateInvite.status
    ).where(
        CandidateInvite.interview_id == interview_id,
        CandidateInvite.status != InviteStatus.FINISHED,
    )

    async with Session() as session:
        return [tuple(row) for row in await session.execute(query)]


async def get(invite_id: uuid.UUID) -> CandidateInvite | None:
    async with Session() as session:
        return await session.get(CandidateInvite, invite_id)


async def expiring(before: datetime, limit: int) -> list[CandidateInvite]:
    """Up to `limit` invites never started and last sent before `before`."""
    async with Session() as session:
        rows = await session.scalars(
            select(CandidateInvite)
            .where(
                CandidateInvite.status.in_([InviteStatus.INVITED, InviteStatus.UNDELIVERED]),
                CandidateInvite.sent_at < before,
            )
            .order_by(CandidateInvite.sent_at)
            .limit(limit)
        )

        return list(rows)


async def mark_expired(invite_id: uuid.UUID, before: datetime) -> bool:
    """Expires an invite that still hasn't started and wasn't sent again since `before`; False
    when it was started or sent again meanwhile."""
    async with Session() as session:
        marked = await session.scalar(
            update(CandidateInvite)
            .where(
                CandidateInvite.id == invite_id,
                CandidateInvite.status.in_([InviteStatus.INVITED, InviteStatus.UNDELIVERED]),
                CandidateInvite.sent_at < before,
            )
            .values(status=InviteStatus.EXPIRED)
            .returning(CandidateInvite.id)
        )
        await session.commit()

    return marked is not None


async def get_by_token(token: str) -> tuple[CandidateInvite, Interview] | None:
    query = (
        select(CandidateInvite, Interview)
        .join(Interview, Interview.id == CandidateInvite.interview_id)
        .where(CandidateInvite.token == token)
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

        return tuple(row) if row else None


async def start(invite_id: uuid.UUID, user_id: str) -> bool:
    """Marks the invite in process, an expired one too (a candidate back through the test's
    link). False when it's gone: revoked meanwhile."""
    async with Session() as session:
        stored = await session.get(CandidateInvite, invite_id, with_for_update=True)

        if stored is None:
            return False

        stored.user_id = user_id

        if stored.status in NOT_STARTED:
            stored.status = InviteStatus.IN_PROCESS

        await session.commit()

    return True


async def mark_undelivered(invite_id: uuid.UUID, notice: dict) -> None:
    """Only an unused invite: a candidate who has started got the email after all. The
    company's notification is saved only when the invite changes, so a repeat sends none."""
    async with Session() as session:
        marked = await session.scalar(
            update(CandidateInvite)
            .where(
                CandidateInvite.id == invite_id,
                CandidateInvite.status == InviteStatus.INVITED,
            )
            .values(status=InviteStatus.UNDELIVERED)
            .returning(CandidateInvite.id)
        )

        if marked is not None:
            outbox.add(session, OutboxEvent, NOTIFICATION_REQUESTED, notice)

        await session.commit()


async def finish(
    invite_id: uuid.UUID, grade: int | None, flagged: bool, notice: dict | None
) -> None:
    """Marks the invite finished (the candidates list may have already) with the candidate's
    grade and integrity flag, and the company's notification, if any."""
    async with Session() as session:
        await session.execute(
            update(CandidateInvite)
            .where(CandidateInvite.id == invite_id)
            .values(status=InviteStatus.FINISHED, grade=grade, flagged=flagged)
        )

        if notice:
            outbox.add(session, OutboxEvent, NOTIFICATION_REQUESTED, notice)

        await session.commit()


async def remove(invite_id: uuid.UUID) -> None:
    """Deletes the invite; its link stops working."""
    async with Session() as session:
        await session.execute(delete(CandidateInvite).where(CandidateInvite.id == invite_id))
        await session.commit()


async def set_extra_time(invite_id: uuid.UUID, extra_time: int) -> None:
    async with Session() as session:
        await session.execute(
            update(CandidateInvite)
            .where(CandidateInvite.id == invite_id)
            .values(extra_time=extra_time)
        )
        await session.commit()
