import uuid
from datetime import UTC, datetime, timedelta

from prepza_common.constants import DELETED_USER
from sqlalchemy import func, select, update

from app.constants.audit import AuditAction
from app.models.audit import AuditEvent
from app.storage import accounts, audit, companies
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


def test_a_deleted_users_decisions_are_exported_then_stay_without_their_id(run):
    user = f"gone-{uuid.uuid4()}"

    async def scenario():
        name = f"Audit {uuid.uuid4()}"
        company = await companies.create(name, "owner", "owner@example.com")
        await audit.record(company.id, user, AuditAction.RESULTS_VIEWED)
        await audit.record(company.id, "owner", AuditAction.TOPICS_APPROVED)
        exported = (await accounts.export(user, "gone@example.com"))["company_decisions"]
        await audit.forget_user(user)
        # Safe to repeat.
        await audit.forget_user(user)
        listed = await audit.list_for_company(company.id, 0, 10)
        left = (await accounts.export(user, "gone@example.com"))["company_decisions"]
        await companies.delete(company.id)

        return name, exported, listed, left

    name, exported, listed, left = run(scenario())

    assert [(row["company"], row["action"]) for row in exported] == [
        (name, AuditAction.RESULTS_VIEWED)
    ]
    assert sorted(row.user_id for row in listed) == sorted([DELETED_USER, "owner"])
    assert left == []
