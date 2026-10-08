import secrets
import uuid
from datetime import UTC, datetime

from prepza_common import outbox
from prepza_common.notifications import NOTIFICATION_REQUESTED
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.events import CANDIDATE_FINISHED, CANDIDATE_INVITED, CANDIDATE_REMOVED
from app.constants.invites import NOT_STARTED, InviteStatus
from app.models.interviews import Interview
from app.models.invites import CandidateInvite
from app.models.outbox import OutboxEvent
from app.storage import processed_events
from app.storage.db import Session


async def upsert(
    interview_id,
    email: str,
    title: str,
    company: str,
    language: str,
    logo_path: str | None = None,
    hold_key: str | None = None,
) -> tuple[CandidateInvite, bool]:
    """Creates the invite (with `hold_key`, its credits' key), or returns the existing one so it
    can be sent again, and saves the email's event with it. True when it revived an expired
    invite, whose credits were given back."""
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
            hold_key=hold_key,
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

        revived = invite.status == InviteStatus.EXPIRED

        # Sending again revives an undelivered or expired invite and restarts its 30 days.
        if invite.status in (InviteStatus.UNDELIVERED, InviteStatus.EXPIRED):
            invite.status = InviteStatus.INVITED

        invite.sent_at = datetime.now(UTC)
        invite.reminded_at = None
        company_id = await session.scalar(
            select(Interview.company_id).where(Interview.id == interview_id)
        )

        outbox.add(
            session,
            OutboxEvent,
            CANDIDATE_INVITED,
            {
                "invite_id": str(invite.id),
                # Notifications skips an address that stopped this company's emails.
                "company_id": str(company_id),
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

        return invite, revived


async def for_link(interview_id, email: str, hold_key: str | None = None) -> CandidateInvite:
    """The candidate who came through the test's link: their invite, made now if it's new (with
    `hold_key`, its credits' key). No email goes out: they're already here."""
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
            hold_key=hold_key,
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


async def held(interview_id, email: str) -> tuple[str | None, str | None]:
    """The invite's status and its credits' key, or (None, None) when this email hasn't been
    invited."""
    query = select(CandidateInvite.status, CandidateInvite.hold_key).where(
        CandidateInvite.interview_id == interview_id, CandidateInvite.email == email.lower()
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

    return (row[0], row[1]) if row else (None, None)


async def status_of(interview_id, email: str) -> str | None:
    """The invite's status, or None when this email hasn't been invited."""
    query = select(CandidateInvite.status).where(
        CandidateInvite.interview_id == interview_id, CandidateInvite.email == email.lower()
    )

    async with Session() as session:
        return await session.scalar(query)


async def unfinished(interview_id) -> list[CandidateInvite]:
    """The interview's invites not finished yet."""
    query = select(CandidateInvite).where(
        CandidateInvite.interview_id == interview_id,
        CandidateInvite.status != InviteStatus.FINISHED,
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def get(invite_id: uuid.UUID) -> CandidateInvite | None:
    async with Session() as session:
        return await session.get(CandidateInvite, invite_id)


async def get_by_token(token: str) -> tuple[CandidateInvite, Interview] | None:
    query = (
        select(CandidateInvite, Interview)
        .join(Interview, Interview.id == CandidateInvite.interview_id)
        .where(CandidateInvite.token == token)
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

        return tuple(row) if row else None


async def start(invite_id: uuid.UUID, user_id: str) -> str | None:
    """Marks the invite in process, an expired one too (a candidate back through the test's
    link), and returns its status before. None when it's gone: revoked meanwhile."""
    async with Session() as session:
        stored = await session.get(CandidateInvite, invite_id, with_for_update=True)

        if stored is None:
            return None

        before = stored.status
        stored.user_id = user_id

        if stored.status in NOT_STARTED:
            stored.status = InviteStatus.IN_PROCESS

        await session.commit()

    return before


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
    invite_id: uuid.UUID,
    grade: int | None,
    flagged: bool,
    notice: dict | None,
    event_id: str | None = None,
    result: dict | None = None,
) -> None:
    """Marks the invite finished (the candidates list may have already) with the candidate's
    grade and integrity flag, and the company's notification and the candidate.finished event
    (`result`), if any: once per event."""
    async with Session() as session:
        new = await processed_events.claim(session, event_id)
        await session.execute(
            update(CandidateInvite)
            .where(CandidateInvite.id == invite_id)
            .values(status=InviteStatus.FINISHED, grade=grade, flagged=flagged)
        )

        if notice and new:
            outbox.add(session, OutboxEvent, NOTIFICATION_REQUESTED, notice)

        if result and new:
            outbox.add(session, OutboxEvent, CANDIDATE_FINISHED, result)

        await session.commit()


async def remove(invite: CandidateInvite, company_id) -> str | None:
    """Deletes the invite (its link stops working) and tells the other services, which forget the
    candidate too: the company's notifications about them, the ATS's record of them. Returns its
    status as it was deleted."""
    async with Session() as session:
        removed = await session.scalar(
            delete(CandidateInvite)
            .where(CandidateInvite.id == invite.id)
            .returning(CandidateInvite.status)
        )
        outbox.add(
            session,
            OutboxEvent,
            CANDIDATE_REMOVED,
            {
                "company_id": str(company_id),
                "interview_id": str(invite.interview_id),
                "email": invite.email,
            },
        )
        await session.commit()

    return removed


async def set_extra_time(invite_id: uuid.UUID, extra_time: int) -> None:
    async with Session() as session:
        await session.execute(
            update(CandidateInvite)
            .where(CandidateInvite.id == invite_id)
            .values(extra_time=extra_time)
        )
        await session.commit()
