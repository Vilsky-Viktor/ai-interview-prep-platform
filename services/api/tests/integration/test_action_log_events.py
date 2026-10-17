"""A member's web hook actions reach the company's action log through api's outbox, saved with
the change itself; the web hook is named by its site only. (API keys: test_key_permissions.)"""

import uuid

from prepza_common.audit_actions import AUDIT_RECORDED
from sqlalchemy import select

from app.models.outbox import OutboxEvent
from app.storage import webhooks
from app.storage.db import Session


async def logged(company) -> list[dict]:
    """The company's actions waiting in the outbox for its action log, oldest first."""
    query = (
        select(OutboxEvent.data)
        .where(
            OutboxEvent.event_type == AUDIT_RECORDED,
            OutboxEvent.data["company_id"].astext == str(company),
        )
        .order_by(OutboxEvent.created_at)
    )

    async with Session() as session:
        return list(await session.scalars(query))


def test_a_web_hook_added_tested_and_deleted_is_logged_by_its_site(run):
    company = uuid.uuid4()

    async def scenario():
        hook = await webhooks.add(company, "https://hooks.zapier.com/secret/path", "s", "ann", 5)
        await webhooks.tested(hook, "bob")
        await webhooks.remove(company, hook.id, "ann")
        # Gone already: nothing more.
        await webhooks.remove(company, hook.id, "ann")

        return hook, await logged(company)

    hook, events = run(scenario())

    assert [(row["action"], row["user_id"], row["target_label"]) for row in events] == [
        ("webhook_added", "ann", "https://hooks.zapier.com/…"),
        ("webhook_tested", "bob", "https://hooks.zapier.com/…"),
        ("webhook_deleted", "ann", "https://hooks.zapier.com/…"),
    ]
    assert {(row["target_kind"], row["target_id"]) for row in events} == {("webhook", str(hook.id))}
