import asyncio
from datetime import UTC, datetime, timedelta

from app.constants.api import RETRY_FIRST_DELAY, RETRY_GIVE_UP, RETRY_MAX_DELAY
from app.helpers.webhooks import retry_delay
from app.services import webhooks as delivery
from tests.unit.test_webhook_delivery import finish


def due(endpoints, hook, event_id="e1", age=timedelta(minutes=5)):
    """The kept event's time came; it was first kept `age` ago."""
    row = endpoints["retries"][(hook.id, event_id)]
    row.next_at = datetime.now(UTC) - timedelta(seconds=1)
    row.created_at = datetime.now(UTC) - age

    return row


def run():
    return asyncio.run(delivery.retry())


def failed_once(endpoints, url="https://down.example/x"):
    hook = endpoints["hook"](url)
    endpoints["failing"].add(url)
    finish()

    return hook


def test_the_wait_doubles_up_to_a_limit():
    assert retry_delay(1) == RETRY_FIRST_DELAY
    assert retry_delay(2) == RETRY_FIRST_DELAY * 2
    assert retry_delay(3) == RETRY_FIRST_DELAY * 4
    assert retry_delay(30) == RETRY_MAX_DELAY


def test_an_event_isnt_sent_again_before_its_time(endpoints):
    failed_once(endpoints)
    endpoints["failing"].clear()

    assert run() == 0
    assert endpoints["posted"] == []


def test_an_event_sent_again_and_taken_is_done(endpoints):
    hook = failed_once(endpoints)
    endpoints["failing"].clear()
    due(endpoints, hook)

    assert run() == 1

    ((url, body, signature),) = endpoints["posted"]

    assert url == "https://down.example/x" and body["id"] == "e1"
    assert signature.startswith("t=")
    assert endpoints["retries"] == {}
    assert (hook.id, "e1") in endpoints["delivered"]

    # A redelivered event doesn't send it again.
    finish()

    assert len(endpoints["posted"]) == 1


def test_an_event_that_fails_again_waits_twice_as_long(endpoints):
    hook = failed_once(endpoints)
    due(endpoints, hook)
    run()
    row = endpoints["retries"][(hook.id, "e1")]
    wait = row.next_at - datetime.now(UTC)

    assert row.attempts == 2
    assert RETRY_FIRST_DELAY * 2 - timedelta(minutes=1) < wait <= RETRY_FIRST_DELAY * 2
    assert hook.failing is False


def test_after_days_of_failing_the_event_is_dropped_and_the_web_hook_shows_as_failing(endpoints):
    hook = failed_once(endpoints)
    due(endpoints, hook, age=RETRY_GIVE_UP)
    run()

    assert endpoints["retries"] == {}
    assert hook.failing is True

    # The next event it takes clears it.
    endpoints["failing"].clear()
    finish("e2")

    assert hook.failing is False


def test_an_event_with_nowhere_to_go_any_more_is_dropped_unsent(endpoints, companies_api):
    left = failed_once(endpoints, "https://left.example/x")
    got = failed_once(endpoints, "https://got.example/x")
    endpoints["failing"].clear()
    left.created_by = "u2"
    companies_api["roles"]["u2"] = "viewer"
    endpoints["delivered"].add((got.id, "e1"))
    due(endpoints, left)
    due(endpoints, got)

    assert run() == 2
    assert endpoints["posted"] == []
    assert endpoints["retries"] == {}


def test_the_schedule_sends_kept_events_again(client, monkeypatch):
    runs = []

    async def retry():
        runs.append(True)

        return 1

    monkeypatch.setattr(delivery, "retry", retry)

    assert client.post("/internal/schedules/webhook-retries").status_code == 204
    assert runs == [True]
