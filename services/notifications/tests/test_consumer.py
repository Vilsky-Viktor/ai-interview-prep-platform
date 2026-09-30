import asyncio
import json

from app.constants.events import (
    ATTEMPTS_KEY,
    CONSUMER_GROUP,
    DEAD_LETTER_STREAM,
    EVENTS_STREAM,
    MAX_ATTEMPTS,
    PREPARATION_SHARED,
)
from app.helpers.emails import candidate_invite_email, share_invite_email
from app.integrations import smtp
from app.services import consumer

DATA = {"email": "bob@example.com", "token": "abc", "title": "Backend", "inviter": "Ann"}


class FakeRedis:
    def __init__(self):
        self.acked = []
        self.attempts: dict[str, int] = {}
        self.dead = []

    async def xack(self, stream, group, entry_id):
        self.acked.append((stream, group, entry_id))

    async def hincrby(self, key, field, amount):
        assert key == ATTEMPTS_KEY
        self.attempts[field] = self.attempts.get(field, 0) + amount

        return self.attempts[field]

    async def hdel(self, key, field):
        self.attempts.pop(field, None)

    async def xadd(self, stream, fields, maxlen, approximate):
        self.dead.append((stream, fields))


def fields(event_type=PREPARATION_SHARED):
    return {"type": event_type, "data": json.dumps(DATA)}


def test_candidate_invite_email():
    data = {
        "email": "bob@example.com",
        "token": "xyz",
        "title": "Backend",
        "company": "Acme",
    }
    message = candidate_invite_email(data, "http://localhost:8090", "prepza. <no-reply@prepza.local>")

    assert message["To"] == "bob@example.com"
    assert message["Subject"] == "Acme invited you to an interview on prepza."
    assert "http://localhost:8090/invite/xyz" in message.get_content()


def test_share_invite_email():
    message = share_invite_email(DATA, "http://localhost:8090/", "prepza. <no-reply@prepza.local>")

    assert message["To"] == "bob@example.com"
    assert message["Subject"] == "Ann shared “Backend” with you on prepza."
    assert "http://localhost:8090/share/abc" in message.get_content()


def test_sends_and_acknowledges(monkeypatch):
    sent = []

    async def fake_send(message):
        sent.append(message["To"])

    monkeypatch.setattr(smtp, "send", fake_send)
    redis = FakeRedis()

    asyncio.run(consumer.process(redis, "1-0", fields()))

    assert sent == ["bob@example.com"]
    assert redis.acked == [(EVENTS_STREAM, CONSUMER_GROUP, "1-0")]


def test_failed_send_stays_pending(monkeypatch):
    async def failing_send(message):
        raise ConnectionError("SMTP is down")

    monkeypatch.setattr(smtp, "send", failing_send)
    redis = FakeRedis()

    asyncio.run(consumer.process(redis, "1-0", fields()))

    assert redis.acked == []
    assert redis.attempts == {"1-0": 1}


def test_event_moves_to_dead_letters_after_max_attempts(monkeypatch):
    async def failing_send(message):
        raise ConnectionError("SMTP is down")

    monkeypatch.setattr(smtp, "send", failing_send)
    redis = FakeRedis()

    for _ in range(MAX_ATTEMPTS):
        asyncio.run(consumer.process(redis, "1-0", fields()))

    assert redis.acked == [(EVENTS_STREAM, CONSUMER_GROUP, "1-0")]
    assert [stream for stream, _ in redis.dead] == [DEAD_LETTER_STREAM]
    assert redis.dead[0][1]["entry_id"] == "1-0"
    assert redis.attempts == {}


def test_unknown_events_are_acknowledged(monkeypatch):
    redis = FakeRedis()

    asyncio.run(consumer.process(redis, "2-0", fields("something.else")))

    assert redis.acked == [(EVENTS_STREAM, CONSUMER_GROUP, "2-0")]
