import asyncio

from prepza_common import analytics


def test_events_carry_a_pseudonym_and_never_break_the_caller(monkeypatch):
    sent = []

    async def fake_publish(event_type, data):
        sent.append((event_type, data))

    async def broken(event_type, data):
        raise RuntimeError("pubsub down")

    monkeypatch.setenv("ANALYTICS_SALT", "salt")
    monkeypatch.setattr(analytics, "publish", fake_publish)
    asyncio.run(analytics.track("test_ready", user_id="ann", topics=7))

    [(event_type, data)] = sent
    assert event_type == "funnel.test_ready"
    assert data["user"] == analytics.pseudonym("ann") != "ann"
    assert data["props"] == {"topics": 7}

    monkeypatch.setattr(analytics, "publish", broken)
    asyncio.run(analytics.track("test_ready", user_id="ann"))


def test_the_same_user_gets_the_same_pseudonym_only_with_the_same_salt(monkeypatch):
    monkeypatch.setenv("ANALYTICS_SALT", "one")
    first = analytics.pseudonym("ann")
    monkeypatch.setenv("ANALYTICS_SALT", "two")

    assert analytics.pseudonym("ann") != first
