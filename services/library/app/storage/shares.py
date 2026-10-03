import secrets
import uuid
from datetime import UTC, datetime

from prepza_common import outbox
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert

from app.constants.events import PREPARATION_SHARED
from app.models.outbox import OutboxEvent
from app.models.sets import QuestionSet
from app.models.sharing import ShareInvite
from app.storage import stats
from app.storage.db import Session
from app.storage.joins import join_statement


async def upsert(
    set_id: uuid.UUID, email: str, invited_by: str, title: str, inviter: str, language: str
) -> ShareInvite:
    """Creates the invite, or returns the existing one so it can be sent again, and saves the
    email's event with it; the email goes out in the kit's language."""
    statement = (
        insert(ShareInvite)
        .values(
            id=uuid.uuid4(),
            set_id=set_id,
            email=email,
            token=secrets.token_urlsafe(32),
            invited_by=invited_by,
            created_at=datetime.now(UTC),
        )
        .on_conflict_do_nothing()
    )

    async with Session() as session:
        await session.execute(statement)
        invite = await session.scalar(
            select(ShareInvite).where(ShareInvite.set_id == set_id, ShareInvite.email == email)
        )
        invite.undelivered_at = None
        outbox.add(
            session,
            OutboxEvent,
            PREPARATION_SHARED,
            {
                "share_id": str(invite.id),
                "email": invite.email,
                "token": invite.token,
                "title": title,
                "inviter": inviter,
                "language": language,
            },
        )
        await session.commit()

        return invite


async def is_invited(set_id: uuid.UUID, email: str) -> bool:
    query = select(ShareInvite.id).where(ShareInvite.set_id == set_id, ShareInvite.email == email)

    async with Session() as session:
        return await session.scalar(query.limit(1)) is not None


async def accepted_by(set_id: uuid.UUID, user_id: str) -> bool:
    """Whether the user joined the kit through the owner's invite."""
    query = select(ShareInvite.id).where(
        ShareInvite.set_id == set_id, ShareInvite.accepted_by == user_id
    )

    async with Session() as session:
        return await session.scalar(query.limit(1)) is not None


async def count_for_set(set_id: uuid.UUID) -> int:
    """People the kit is shared with: accepted and pending invites."""
    query = select(func.count()).select_from(ShareInvite).where(ShareInvite.set_id == set_id)

    async with Session() as session:
        return await session.scalar(query)


async def list_for_set(set_id: uuid.UUID, offset: int, limit: int) -> list[ShareInvite]:
    query = (
        select(ShareInvite)
        .where(ShareInvite.set_id == set_id)
        .order_by(ShareInvite.created_at.desc(), ShareInvite.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def get_by_token(token: str) -> tuple[ShareInvite, QuestionSet] | None:
    query = (
        select(ShareInvite, QuestionSet)
        .join(QuestionSet, QuestionSet.id == ShareInvite.set_id)
        .where(ShareInvite.token == token)
    )

    async with Session() as session:
        row = (await session.execute(query)).first()

        return tuple(row) if row else None


async def mark_undelivered(share_id: uuid.UUID) -> None:
    """Only an invite nobody has accepted: whoever accepted it got the email after all."""
    async with Session() as session:
        await session.execute(
            update(ShareInvite)
            .where(ShareInvite.id == share_id, ShareInvite.accepted_by.is_(None))
            .values(undelivered_at=datetime.now(UTC))
        )
        await session.commit()


async def accept(invite: ShareInvite, user_id: str) -> None:
    """Marks the invite accepted and joins the user, in one transaction."""
    async with Session() as session:
        invite = await session.get(ShareInvite, invite.id)
        invite.accepted_by = user_id
        await session.execute(join_statement(invite.set_id, user_id))
        await stats.recount(session, invite.set_id)
        await session.commit()
