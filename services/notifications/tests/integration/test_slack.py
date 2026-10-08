import pytest
from prepza_common.encryption import encrypt

from app.config.settings import settings
from app.constants.slack import SlackStatus
from app.integrations import companies
from app.integrations import slack as slack_api
from app.storage import slack as storage
from tests.integration.factories import api, company, finished, push

KEY = "Zm9vYmFyYmF6cXV4cXV1eGNvcmdlZ3JhdWx0Z2FycGw="


async def editor(company_id, user_id):
    return {"member": True, "editor": True}


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    """Slack set up on the server; what's posted and which apps are removed, without Slack."""
    found = {"posted": [], "revoked": []}

    async def post(webhook, text):
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
