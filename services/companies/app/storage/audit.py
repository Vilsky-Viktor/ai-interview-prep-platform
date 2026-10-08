from datetime import datetime

from prepza_common.constants import DELETED_USER
from sqlalchemy import delete, select, update

from app.models.audit import AuditEvent
from app.storage.db import Session


async def record(
    company_id, user_id: str, action: str, target_id=None, via: str | None = None
) -> None:
    async with Session() as session:
        session.add(
            AuditEvent(
                company_id=company_id, user_id=user_id, action=action, target_id=target_id, via=via
            )
        )
        await session.commit()


async def list_for_company(company_id, offset: int, limit: int) -> list[AuditEvent]:
    """Newest first."""
    query = (
        select(AuditEvent)
        .where(AuditEvent.company_id == company_id)
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id)
        .offset(offset)
        .limit(limit)
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def forget_user(user_id: str) -> None:
    """The user's decisions stay in their companies' logs, without the user's id."""
    query = update(AuditEvent).where(AuditEvent.user_id == user_id).values(user_id=DELETED_USER)

    async with Session() as session:
        await session.execute(query)
        await session.commit()


async def delete_before(before: datetime) -> int:
    async with Session() as session:
        result = await session.execute(delete(AuditEvent).where(AuditEvent.created_at < before))
        await session.commit()

        return result.rowcount
