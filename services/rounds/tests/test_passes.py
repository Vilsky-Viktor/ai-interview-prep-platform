import uuid

import pytest

from app.auth import current_user
from app.main import app
from app.schemas.user import User
from app.storage import certificates, rounds

PREPARATION_ID = uuid.uuid4()
TOPIC_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def clear_overrides(monkeypatch):
    async def fake_answered(user_id, preparation_id):
        return {(TOPIC_ID, "open"): 7}

    monkeypatch.setattr("app.routers.preparations.answered_counts", fake_answered)
    yield
    app.dependency_overrides.clear()


def sign_in():
    app.dependency_overrides[current_user] = lambda: User(
        uid="member", email="member@example.com", email_verified=True, name="Ann"
    )


def no_certificates(monkeypatch):
    async def fake_certs(user_id, preparation_id):
        return {}

    monkeypatch.setattr(certificates, "for_preparation", fake_certs)


def test_lists_best_scores(client, monkeypatch):
    async def fake_best(user_id, preparation_id):
        assert user_id == "member"
        assert preparation_id == PREPARATION_ID

        return [(TOPIC_ID, "open", 92), (TOPIC_ID, "choice", 50)]

    monkeypatch.setattr(rounds, "best_for_preparation", fake_best)
    no_certificates(monkeypatch)
    sign_in()

    response = client.get(f"/preparations/{PREPARATION_ID}/passes")

    assert response.status_code == 200
    assert response.json() == [
        {
            "topic_id": str(TOPIC_ID),
            "mode": "open",
            "score": 92,
            "answered": 7,
            "certificate_id": None,
        },
        {
            "topic_id": str(TOPIC_ID),
            "mode": "choice",
            "score": 50,
            "answered": 0,
            "certificate_id": None,
        },
    ]


def test_lists_empty_when_none_finished(client, monkeypatch):
    async def fake_best(user_id, preparation_id):
        return []

    monkeypatch.setattr(rounds, "best_for_preparation", fake_best)
    no_certificates(monkeypatch)
    sign_in()

    response = client.get(f"/preparations/{PREPARATION_ID}/passes")

    assert response.status_code == 200
    assert response.json() == []


def test_includes_certificate_id(client, monkeypatch):
    cert_id = uuid.uuid4()

    async def fake_best(user_id, preparation_id):
        return [(TOPIC_ID, "open", 92), (TOPIC_ID, "choice", 50)]

    async def fake_certs(user_id, preparation_id):
        assert user_id == "member"
        assert preparation_id == PREPARATION_ID

        return {TOPIC_ID: cert_id}

    monkeypatch.setattr(rounds, "best_for_preparation", fake_best)
    monkeypatch.setattr(certificates, "for_preparation", fake_certs)
    sign_in()

    response = client.get(f"/preparations/{PREPARATION_ID}/passes")

    assert response.status_code == 200
    assert response.json() == [
        {
            "topic_id": str(TOPIC_ID),
            "mode": "open",
            "score": 92,
            "answered": 7,
            "certificate_id": str(cert_id),
        },
        {
            "topic_id": str(TOPIC_ID),
            "mode": "choice",
            "score": 50,
            "answered": 0,
            "certificate_id": str(cert_id),
        },
    ]


def test_lists_mastered_topics_for_user(client, monkeypatch):
    other_prep = uuid.uuid4()
    other_topic = uuid.uuid4()

    async def fake_mastered(user_id):
        assert user_id == "member"

        return [(PREPARATION_ID, TOPIC_ID), (other_prep, other_topic)]

    monkeypatch.setattr(certificates, "mastered_topics", fake_mastered)
    sign_in()

    response = client.get("/preparations/mastered")

    assert response.status_code == 200
    assert response.json() == [
        {"preparation_id": str(PREPARATION_ID), "topic_id": str(TOPIC_ID)},
        {"preparation_id": str(other_prep), "topic_id": str(other_topic)},
    ]
