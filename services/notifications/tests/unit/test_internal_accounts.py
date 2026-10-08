from prepza_common.service_auth import issue_token

from app.models.slack import SlackConnection
from app.storage import notifications, slack

HEADERS = {
    "Authorization": f"Bearer {issue_token('library', 'notifications', 'test-secret-that-is-at-least-32-bytes')}"
}


def test_deleting_an_account_reads_the_email_from_the_body_and_forgets_their_channels(
    client, monkeypatch
):
    done = []

    async def remove_user(user_id):
        done.append(("own", user_id))

    async def remove_candidate(email):
        done.append(("candidate", email))

    async def forget_maker(user_id):
        done.append(("slack", user_id))

    monkeypatch.setattr(notifications, "remove_user", remove_user)
    monkeypatch.setattr(notifications, "remove_candidate", remove_candidate)
    monkeypatch.setattr(slack, "forget_maker", forget_maker)

    response = client.request(
        "DELETE", "/internal/users/u1", json={"email": "ann@example.com"}, headers=HEADERS
    )

    assert response.status_code == 204
    assert done == [("own", "u1"), ("candidate", "ann@example.com"), ("slack", "u1")]


def test_an_export_holds_the_slack_channels_they_connected(client, monkeypatch):
    async def latest(recipients, limit):
        return []

    async def made_by(user_id):
        return [SlackConnection(company_id="c1", team="Acme", channel="#hiring", created_at=None)]

    monkeypatch.setattr(notifications, "latest", latest)
    monkeypatch.setattr(slack, "made_by", made_by)

    response = client.post("/internal/users/u1/export", headers=HEADERS)

    assert response.json() == {
        "notifications": [],
        "slack_channels": [{"company_id": "c1", "team": "Acme", "channel": "#hiring", "at": None}],
    }
