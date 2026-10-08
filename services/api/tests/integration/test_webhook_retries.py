import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from app.constants.api import RETRY_LEASE
from app.storage import webhook_retries as retries
from app.storage import webhooks


def test_an_event_is_kept_once_and_claimed_by_one_run_at_a_time(run):
    company = uuid.uuid4()
    past = datetime.now(UTC) - timedelta(seconds=1)

    async def scenario():
        hook = await webhooks.add(company, "https://example.com/x", "sealed", "u1")
        later = await webhooks.add(company, "https://example.com/y", "sealed", "u1")
        # Twice: a redelivered event keeps the retry it has.
        await retries.add(hook.id, "e1", '{"id":"e1"}', past)
        await retries.add(hook.id, "e1", '{"id":"other"}', past)
        await retries.add(later.id, "e1", '{"id":"e1"}', datetime.now(UTC) + timedelta(hours=1))
        # Two runs at once: each kept event goes to one of them.
        first, second = await asyncio.gather(retries.claim(25), retries.claim(25))

        return hook, first + second, await retries.claim(25)

    hook, claimed, again = run(scenario())
    ((row, found),) = claimed

    assert found.id == hook.id and found.url == "https://example.com/x"
    assert row.event_id == "e1" and row.body == '{"id":"e1"}' and row.attempts == 1
    # Put off while it's being sent, so a run cut off midway leaves it for a later one.
    assert row.next_at > datetime.now(UTC) + RETRY_LEASE - timedelta(minutes=1)
    assert again == []


def test_a_kept_event_waits_longer_goes_once_sent_and_with_its_web_hook(run):
    company = uuid.uuid4()
    past = datetime.now(UTC) - timedelta(seconds=1)

    async def scenario():
        hook = await webhooks.add(company, "https://example.com/x", "sealed", "u1")
        await retries.add(hook.id, "e1", "{}", past)
        await retries.add(hook.id, "e2", "{}", past)
        await retries.add(hook.id, "e3", "{}", past)
        await retries.postpone(hook.id, "e1", 2, past)
        await retries.remove(hook.id, "e2")
        claimed = await retries.claim(25)
        await retries.add(hook.id, "e4", "{}", past)
        await webhooks.remove(company, hook.id)

        return claimed, await retries.claim(25)

    claimed, after = run(scenario())

    assert sorted((row.event_id, row.attempts) for row, _ in claimed) == [("e1", 2), ("e3", 1)]
    assert after == []


def test_a_web_hook_shows_as_failing_until_cleared(run):
    company = uuid.uuid4()

    async def scenario():
        hook = await webhooks.add(company, "https://example.com/x", "sealed", "u1")
        fresh = (await webhooks.of_company(company))[0].failing
        await webhooks.set_failing(hook.id, True)
        failing = (await webhooks.of_company(company))[0].failing
        await webhooks.set_failing(hook.id, False)

        return fresh, failing, (await webhooks.of_company(company))[0].failing

    assert run(scenario()) == (False, True, False)
