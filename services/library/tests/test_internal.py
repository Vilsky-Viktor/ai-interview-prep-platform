import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.storage import preparations

PAYLOAD = {
    "owner_uid": "user-1",
    "source_text": "Job",
    "title": "Backend",
    "level": "medium",
    "requirements": ["Python"],
    "topics": [],
}


def token(secret="test-secret-that-is-at-least-32-bytes", lifetime=60):
    exp = datetime.now(UTC) + timedelta(seconds=lifetime)

    return jwt.encode({"iss": "generation", "exp": exp}, secret, algorithm="HS256")


def post(client, value):
    return client.post(
        "/internal/preparations", json=PAYLOAD, headers={"Authorization": f"Bearer {value}"}
    )


def test_create_with_service_token(client, monkeypatch):
    new_id = uuid.uuid4()

    async def fake_create(preparation):
        return new_id

    monkeypatch.setattr(preparations, "create", fake_create)

    response = post(client, token())

    assert response.status_code == 201
    assert response.json() == {"id": str(new_id)}


def test_rejects_wrong_secret(client):
    assert post(client, token(secret="another-secret-that-is-32-bytes-long")).status_code == 401


def test_rejects_expired_token(client):
    assert post(client, token(lifetime=-10)).status_code == 401
