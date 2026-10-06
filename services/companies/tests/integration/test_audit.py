import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, update

from app.constants.audit import AuditAction
from app.models.audit import AuditEvent
from app.storage import audit, companies
from app.storage.db import Session


def test_audit_events_list_newest_first_age_out_and_go_with_the_company(run):
    target = uuid.uuid4()

    async def scenario():
        company = await companies.create(f"Audit {uuid.uuid4()}", "ann", "ann@example.com")
        await audit.record(company.id, "ann", AuditAction.PASS_MARK_CHANGED, target)
        await audit.record(company.id, "ann", AuditAction.RESULTS_VIEWED, target)
        await audit.record(company.id, "ann", AuditAction.TOPICS_APPROVED)
        listed = await audit.list_for_company(company.id, 0, 10)
        # The first event is three years old: retention takes it, and only it.
        async with Session() as session:
            await session.execute(
                update(AuditEvent)
                .where(AuditEvent.id == listed[-1].id)
                .values(created_at=datetime.now(UTC) - timedelta(days=3 * 365))
            )
            await session.commit()

        aged = await audit.delete_before(datetime.now(UTC) - timedelta(days=730))
        kept = await audit.list_for_company(company.id, 0, 10)
        await companies.delete(company.id)

        async with Session() as session:
            left = await session.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.company_id == company.id)
            )

        return listed, aged, kept, left

    listed, aged, kept, left = run(scenario())

    assert [row.action for row in listed] == [
        AuditAction.TOPICS_APPROVED,
        AuditAction.RESULTS_VIEWED,
        AuditAction.PASS_MARK_CHANGED,
    ]
    assert listed[0].target_id is None and listed[1].target_id == target
    assert aged >= 1
    assert [row.action for row in kept] == [
        AuditAction.TOPICS_APPROVED,
        AuditAction.RESULTS_VIEWED,
    ]
    assert left == 0
