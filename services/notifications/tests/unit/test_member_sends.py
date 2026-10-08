import asyncio
from datetime import UTC, datetime

import pytest
from prepza_common.notifications import NotificationKind, Recipient, notification

from app.integrations import billing, companies, generation, library
from app.integrations.resend import ResendBusy
from app.services import delivery, digest, events, reminders
from app.storage import notifications, sent_emails

NOW = datetime(2026, 10, 8, 7, 20, tzinfo=UTC)
COMPANY = {
    "id": "c1",
    "name": "Acme",
    "members": [{"user_id": "ann", "editor": True}, {"user_id": "vic", "editor": False}],
}
ON = {
    "candidate_finished": True,
    "invite_undelivered": True,
    "ats_not_invited": True,
    "interview_ready": True,
    "reminders": True,
}


def person(user_id, **preferences):
    return {
        "user_id": user_id,
        "email": f"{user_id}@example.com",
        "language": "en",
        "preferences": {**ON, **preferences},
    }


@pytest.fixture
def world(monkeypatch):
    """Other services, the sent log and delivery, faked; returns what was sent and claimed."""
    state = {
        "sent": [],
        "claims": [],
        "released": [],
        "people": [person("ann"), person("vic")],
        "low": [{"company_id": "c1", "available": 100}],
        "busy": False,
    }

    async def members(company_ids):
        return [COMPANY] if "c1" in company_ids else []

    async def recipients(user_ids):
        return [found for found in state["people"] if found["user_id"] in user_ids]

    async def low_companies():
        return state["low"]

    async def waiting(ready, started):
        return {
            "without_candidates": [{"id": "i1", "company_id": "c1", "title": "Backend"}],
            "being_generated": [],
        }

    async def statuses(ids):
        return []

    async def claim(user_id, kind, today, every_days, items=()):
        state["claims"].append((user_id, kind, today, every_days, list(items)))

        return list(items)

    async def release(user_id, kind, today, items):
        state["released"].append((user_id, kind))

    async def send(email, key):
        if state["busy"]:
            raise ResendBusy()

        state["sent"].append((email, key))

    async def activity(kinds, since, until):
        state["window"] = (since, until)

        return [
            type(
                "N",
                (),
                {
                    "recipient_id": "c1",
                    "kind": "candidate_finished",
                    "link": "/i1",
                    "data": {"title": "Backend"},
                },
            )()
        ]

    async def no_wait(seconds):
        return None

    monkeypatch.setattr(companies, "members", members)
    monkeypatch.setattr(companies, "waiting_interviews", waiting)
    monkeypatch.setattr(library, "recipients", recipients)
    monkeypatch.setattr(billing, "low_companies", low_companies)
    monkeypatch.setattr(generation, "statuses", statuses)
    monkeypatch.setattr(sent_emails, "claim", claim)
    monkeypatch.setattr(sent_emails, "release", release)
    monkeypatch.setattr(delivery, "send", send)
    monkeypatch.setattr(notifications, "companies_activity", activity)
    monkeypatch.setattr("app.services.member_sends.asyncio.sleep", no_wait)

    return state


def test_the_digest_goes_to_every_member_once_a_day_for_the_hours_before_this_one(world):
    sent = asyncio.run(digest.send_digests(NOW))

    assert sent == 2
    assert sorted(email.to for email, _ in world["sent"]) == ["ann@example.com", "vic@example.com"]
    assert world["window"] == (
        datetime(2026, 10, 7, 7, tzinfo=UTC),
        datetime(2026, 10, 8, 7, tzinfo=UTC),
    )
    assert {claim[1:4] for claim in world["claims"]} == {("digest", NOW.date(), 1)}


def test_no_digest_to_a_member_who_turned_its_kinds_off(world):
    world["people"] = [person("ann", candidate_finished=False), person("vic")]

    asyncio.run(digest.send_digests(NOW))

    assert [email.to for email, _ in world["sent"]] == ["vic@example.com"]


def test_reminders_go_to_owners_and_admins_who_get_them_once_a_week(world):
    sent = asyncio.run(reminders.send_reminders(NOW))

    assert sent == 2
    assert [(email.to, email.subject) for email, _ in world["sent"]] == [
        ("ann@example.com", "Your credits are running low"),
        ("ann@example.com", "Waiting for candidates"),
    ]
    # Credits again next week while low; each interview named once.
    assert [claim[1:] for claim in world["claims"]] == [
        ("low_credits", NOW.date(), 7, []),
        ("no_candidates", NOW.date(), 7, ["i1"]),
    ]


def test_no_reminders_to_someone_who_turned_them_off(world):
    world["people"] = [person("ann", reminders=False)]

    assert asyncio.run(reminders.send_reminders(NOW)) == 0
    assert world["claims"] == []


def test_a_send_over_resends_limit_is_taken_back_for_the_next_run(world):
    world["busy"] = True

    with pytest.raises(ResendBusy):
        asyncio.run(reminders.send_reminders(NOW))

    assert world["released"] == [("ann", "low_credits")]


def test_the_schedules_stop_quietly_when_resend_is_busy(client, world):
    world["busy"] = True

    assert client.post("/internal/schedules/digest").status_code == 204


def test_a_failed_top_up_emails_the_companys_owners_and_admins_at_once(world, monkeypatch):
    async def stored(key, data):
        return True

    async def nothing(*args):
        return None

    monkeypatch.setattr(notifications, "add", stored)
    monkeypatch.setattr(events, "announce", nothing)
    monkeypatch.setattr(events.slack, "deliver", nothing)
    event = notification(Recipient.COMPANY, "c1", NotificationKind.AUTO_TOP_UP_FAILED, "/top-up")

    asyncio.run(events.notify(event, "e-1"))
    asyncio.run(events.notify(event, "e-1"))

    # Viewers can't top up. A retry has the same key, so Resend sends it once.
    assert [(email.to, key) for email, key in world["sent"]] == [
        ("ann@example.com", "events/e-1/ann"),
        ("ann@example.com", "events/e-1/ann"),
    ]
    assert world["sent"][0][0].headers == {}


def test_other_notifications_email_nobody(world, monkeypatch):
    async def stored(key, data):
        return True

    async def nothing(*args):
        return None

    monkeypatch.setattr(notifications, "add", stored)
    monkeypatch.setattr(events, "announce", nothing)
    monkeypatch.setattr(events.slack, "deliver", nothing)
    event = notification(
        Recipient.COMPANY, "c1", NotificationKind.CANDIDATE_FINISHED, "/", title="x"
    )

    asyncio.run(events.notify(event, "e-2"))

    assert world["sent"] == []
