import asyncio
import contextvars
from types import SimpleNamespace

import httpx
import pytest
from prepza_common import outbox, pubsub
from prepza_common.constants import OUTBOX_MAX_ATTEMPTS


def row(name, attempts=0):
    return SimpleNamespace(
        id=name, event_type=f"{name}.done", data={}, attempts=attempts, published_at=None
    )


def status_error(code):
    request = httpx.Request("POST", "https://pubsub")

    return httpx.HTTPStatusError("refused", request=request, response=httpx.Response(code))


@pytest.fixture
def calls(monkeypatch):
    """Pub/Sub, faked: it rejects any call that carries a "bad" event."""
    sent = []

    async def publish_batch(messages, timeout):
        ids = [message["attributes"]["event_id"] for message in messages]
        sent.append(ids)

        if "bad" in ids:
            raise status_error(400)

    monkeypatch.setattr(pubsub, "publish_batch", publish_batch)

    return sent


def test_a_batch_is_published_in_one_call(calls):
    rows = [row("a"), row("b")]

    asyncio.run(outbox.send(rows, 5))

    assert calls == [["a", "b"]]
    assert all(item.published_at for item in rows)


def test_a_rejected_event_is_counted_alone_and_the_others_still_go(calls):
    good, bad, other = row("a"), row("bad"), row("c")

    asyncio.run(outbox.send([good, bad, other], 5))

    assert calls == [["a", "bad", "c"], ["a"], ["bad"], ["c"]]
    assert good.published_at and other.published_at
    assert bad.published_at is None and bad.attempts == 1


def test_an_event_rejected_too_often_is_parked(calls, caplog):
    bad = row("bad", attempts=OUTBOX_MAX_ATTEMPTS - 1)

    asyncio.run(outbox.send([bad], 5))

    assert bad.attempts == OUTBOX_MAX_ATTEMPTS
    assert "parked" in caplog.text


def test_an_outage_raises_and_counts_against_no_event(monkeypatch):
    async def down(messages, timeout):
        raise status_error(503)

    monkeypatch.setattr(pubsub, "publish_batch", down)
    rows = [row("a"), row("b")]

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(outbox.send(rows, 5))

    assert [item.attempts for item in rows] == [0, 0]


def test_a_quiet_flush_publishes_only_the_events_this_request_saved(monkeypatch):
    flushed = []

    async def flush(sessionmaker, model, ids, timeout):
        flushed.append((ids, timeout))

    monkeypatch.setattr(outbox, "flush", flush)
    session = SimpleNamespace(add=lambda item: None)

    async def request():
        outbox.add(session, SimpleNamespace, "a.done", {})
        outbox.add(session, SimpleNamespace, "b.done", {})
        await outbox.flush_quietly(None, None)
        # Nothing new saved: nothing to publish.
        await outbox.flush_quietly(None, None)

    async def other_request():
        await outbox.flush_quietly(None, None)

    contextvars.Context().run(asyncio.run, request())
    contextvars.Context().run(asyncio.run, other_request())

    [(ids, timeout)] = flushed
    assert len(ids) == 2
    assert timeout == 5
