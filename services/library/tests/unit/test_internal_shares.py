import uuid

from prepza_common.service_auth import issue_token

from app.storage import shares

SHARE_ID = uuid.uuid4()
URL = f"/internal/shares/{SHARE_ID}/undelivered"


def test_notifications_marks_a_share_undelivered(client, monkeypatch):
    marked = []

    async def fake_mark(share_id):
        marked.append(share_id)

    monkeypatch.setattr(shares, "mark_undelivered", fake_mark)
    token = issue_token("notifications", "library", "test-secret-that-is-at-least-32-bytes")

    assert client.post(URL, headers={"Authorization": f"Bearer {token}"}).status_code == 204
    assert marked == [SHARE_ID]


def test_marking_needs_a_service_token(client):
    assert client.post(URL).status_code in (401, 403)
