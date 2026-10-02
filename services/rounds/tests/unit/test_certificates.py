import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

from app.storage import certificates

CERT_ID = uuid.uuid4()
PREP_ID = uuid.uuid4()
ISSUED = datetime(2026, 9, 29, tzinfo=UTC)


def test_returns_public_certificate(client, monkeypatch):
    async def fake_get(certificate_id):
        assert certificate_id == CERT_ID

        return SimpleNamespace(
            id=CERT_ID,
            user_name="Viktor Vilskyi",
            topic_title="Python concurrency",
            score=90,
            issued_at=ISSUED,
            preparation_id=PREP_ID,
        )

    monkeypatch.setattr(certificates, "get", fake_get)

    response = client.get(f"/certificates/{CERT_ID}")

    assert response.status_code == 200
    assert response.json() == {
        "id": str(CERT_ID),
        "user_name": "Viktor Vilskyi",
        "topic_title": "Python concurrency",
        "score": 90,
        "issued_at": "2026-09-29T00:00:00Z",
        "preparation_id": str(PREP_ID),
    }


def test_missing_certificate_is_404(client, monkeypatch):
    async def fake_get(certificate_id):
        return None

    monkeypatch.setattr(certificates, "get", fake_get)

    assert client.get(f"/certificates/{CERT_ID}").status_code == 404
