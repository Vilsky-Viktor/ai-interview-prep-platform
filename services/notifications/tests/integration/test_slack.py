from datetime import UTC, datetime, timedelta

import httpx
import pytest
from prepza_common.encryption import encrypt

from app.config.settings import settings
from app.constants.notifications import KEEP_DAYS
from app.constants.slack import SlackStatus
from app.integrations import companies
from app.integrations import slack as slack_api
from app.models.slack import SlackPost
from app.storage import notifications
from app.storage import slack as storage
from app.storage.db import Session
from tests.integration.factories import api, company, finished, push

KEY = "Zm9vYmFyYmF6cXV4cXV1eGNvcmdlZ3JhdWx0Z2FycGw="


async def editor(company_id, user_id):
    return {"member": True, "editor": True}


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    """Slack set up on the server; what's posted and which apps are removed, without Slack."""
    found = {"posted": [], "revoked": [], "down": False}

    async def post(webhook, text):
        if found["down"]:
            raise httpx.ConnectTimeout("Slack is slow")

        found["posted"].append((webhook, text))

    async def revoke(token):
        found["revoked"].append(token)

    monkeypatch.setattr(settings, "slack_client_id", "client")
    monkeypatch.setattr(settings, "slack_client_secret", "secret")
    monkeypatch.setattr(settings, "slack_encryption_key", KEY)
    monkeypatch.setattr(slack_api, "post", post)
    monkeypatch.setattr(slack_api, "revoke", revoke)
    # Whoever connected the channel is still an editor (companies is another service).
    monkeypatch.setattr(companies, "access", editor)

    return found


async def connect(company_id, channel="#hiring", kinds=("candidate_finished",)):
    await storage.connect(
        company_id,
        "Acme",
        channel,
        encrypt(KEY, f"https://hooks/{channel}"),
        encrypt(KEY, "token"),
        list(kinds),
        "u1",
    )


def test_reconnecting_replaces_the_channel_and_keeps_the_kinds(run):
    company_id = company()

    async def scenario():
        await connect(company_id)
        await storage.set_kinds(company_id, ["interview_ready"])
        await storage.mark_broken(company_id)
        broken = await storage.connected(company_id)
        await connect(company_id, channel="#new", kinds=["candidate_finished"])

        return broken, await storage.get(company_id)

    broken, found = run(scenario())

    assert broken is None
    assert (found.channel, found.status, found.kinds) == (
        "#new",
        SlackStatus.CONNECTED,
        ["interview_ready"],
    )


def test_a_notification_posts_once_however_often_its_event_comes(run, configured):
    company_id = company()
    event = push("notification.requested", finished(company_id, email="a@x.com"), "o-1", "m-s1")

    async def scenario():
        await connect(company_id)

        async with api() as client:
            for _ in range(2):
                await client.post("/internal/events", json=event)

    run(scenario())

    assert [webhook for webhook, text in configured["posted"]] == ["https://hooks/#hiring"]
    assert "a@x.com finished “Backend”" in configured["posted"][0][1]


def test_a_retry_after_slack_was_down_posts_it_without_a_second_bell_notification(run, configured):
    company_id = company()
    event = push("notification.requested", finished(company_id, email="a@x.com"), "o-2", "m-s3")

    async def scenario():
        await connect(company_id)

        async with api() as client:
            configured["down"] = True
            failed = await client.post("/internal/events", json=event)
            configured["down"] = False
            retried = [(await client.post("/internal/events", json=event)) for _ in range(2)]

        bell = await notifications.latest([("company", company_id)], limit=None)

        return failed.status_code, [answer.status_code for answer in retried], len(bell)

    # Pub/Sub retries the failed one; the bell had it from the start.
    assert run(scenario()) == (500, [204, 204], 1)
    assert len(configured["posted"]) == 1


def test_a_deleted_companys_channel_and_app_go(run, configured):
    company_id = company()
    deleted = push("company.deleted", {"company_id": company_id}, message_id="m-s2")

    async def scenario():
        await connect(company_id)

        async with api() as client:
            await client.post("/internal/events", json=deleted)

        return await storage.get(company_id)

    assert run(scenario()) is None
    assert configured["revoked"] == ["token"]


def test_a_slack_mark_is_taken_once_freed_on_failure_and_pruned_when_expired(run):
    old_key, key = f"old-{company()}", f"new-{company()}"

    async def scenario():
        async with Session() as session:
            expired = datetime.now(UTC) - timedelta(days=KEEP_DAYS + 1)
            session.add(SlackPost(event_id=old_key, posted_at=expired))
            await session.commit()

        taken = [await storage.claim(key), await storage.claim(key)]
        await storage.release(key)
        taken.append(await storage.claim(key))

        async with Session() as session:
            return taken, await session.get(SlackPost, old_key)

    assert run(scenario()) == ([True, False, True], None)
