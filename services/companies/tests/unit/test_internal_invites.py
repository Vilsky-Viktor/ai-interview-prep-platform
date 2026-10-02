import uuid

from prepza_common.service_auth import issue_token

from app.storage import invites

INVITE_ID = uuid.uuid4()
URL = f"/internal/invites/{INVITE_ID}/undelivered"


def test_notifications_marks_an_invite_undelivered(client, monkeypatch):
    marked = []

    async def fake_mark(invite_id):
        marked.append(invite_id)

    monkeypatch.setattr(invites, "mark_undelivered", fake_mark)
    token = issue_token("notifications", "companies", "test-secret-that-is-at-least-32-bytes")

    assert client.post(URL, headers={"Authorization": f"Bearer {token}"}).status_code == 204
    assert marked == [INVITE_ID]


def test_marking_needs_a_service_token(client):
    assert client.post(URL).status_code in (401, 403)
