import asyncio
import uuid
from datetime import UTC, datetime

import httpx
import pytest

from app.helpers.unsubscribe import address_hash
from app.schemas.notifications import NotificationOut
from app.services import events, feed, suppression
from app.storage import bulk_recipients, notifications, suppressed


def item(kind, **data):
    return NotificationOut(
        id=uuid.uuid4(), kind=kind, link="/news", data=data, created_at=datetime.now(UTC)
    )


def test_news_is_named_in_the_readers_language_and_a_deleted_post_left_out(monkeypatch):
    asked = []

    async def news_titles(ids, language):
        asked.append((ids, language))

        return {"n1": "Neu: Code-Fragen"}

    monkeypatch.setattr(feed.library, "news_titles", news_titles)
    items = [item("news", news_id="n1", title="New"), item("news", news_id="n2"), item("x")]

    shown = asyncio.run(feed.in_language(items, "de"))

    assert [(one.kind, one.data.get("title")) for one in shown] == [
        ("news", "Neu: Code-Fragen"),
        ("x", None),
    ]
    assert asked == [(["n1", "n2"], "de")]


def test_with_library_down_news_keeps_its_english_title(monkeypatch):
    async def news_titles(ids, language):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(feed.library, "news_titles", news_titles)
    items = [item("news", news_id="n1", title="New")]

    assert asyncio.run(feed.in_language(items, "de")) == items


def test_everyones_notifications_are_the_users_after_their_account_was_made(monkeypatch):
    made = datetime(2026, 10, 1, tzinfo=UTC)
    calls = []

    async def account_created(user_id):
        calls.append(user_id)

        return made

    monkeypatch.setattr(feed.library, "account_created", account_created)
    user = f"u-{uuid.uuid4()}"

    assert asyncio.run(feed.account_created(user)) == made
    assert asyncio.run(feed.account_created(user)) == made
    # Kept: it never changes.
    assert calls == [user]


def test_a_deleted_news_posts_notification_goes(monkeypatch):
    removed = []

    async def remove_news(news_id):
        removed.append(news_id)

    monkeypatch.setattr(notifications, "remove_news", remove_news)

    asyncio.run(events.handle("news.deleted", {"news_id": "n1"}, "e1"))

    assert removed == ["n1"]


@pytest.fixture
def suppressing(monkeypatch):
    state = {"added": [], "complained": []}

    async def add(address, reason):
        state["added"].append((address, reason))

    async def mark_complained(send_id, user_id):
        state["complained"].append((str(send_id), user_id))

    monkeypatch.setattr(suppressed, "add", add)
    monkeypatch.setattr(bulk_recipients, "mark_complained", mark_complained)

    return state


def test_a_bounce_or_complaint_suppresses_a_members_address(suppressing):
    send = str(uuid.uuid4())
    complaint = {
        "type": "email.complained",
        "data": {"to": ["Ann@Example.com"], "tags": {"kind": "updates", "id": "ann", "send": send}},
    }
    bounce = {"type": "email.bounced", "data": {"to": ["bob@example.com"], "tags": {}}}

    asyncio.run(suppression.from_webhook(complaint))
    asyncio.run(suppression.from_webhook(bounce))

    assert suppressing["added"] == [
        (address_hash("ann@example.com"), "complained"),
        (address_hash("bob@example.com"), "bounced"),
    ]
    assert suppressing["complained"] == [(send, "ann")]


def test_a_candidates_invite_or_another_event_suppresses_nothing(suppressing):
    invite = {
        "type": "email.bounced",
        "data": {"to": ["cat@example.com"], "tags": {"kind": "candidate_invite", "id": "i"}},
    }
    delivered = {"type": "email.delivered", "data": {"to": ["cat@example.com"]}}

    asyncio.run(suppression.from_webhook(invite))
    asyncio.run(suppression.from_webhook(delivered))

    assert suppressing["added"] == []
