import uuid

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.main import app
from app.storage import certificates, rounds

PREPARATION_ID = uuid.uuid4()
TOPIC_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def no_open_rounds(monkeypatch):
    async def fake_open(user_id, preparation_id):
        return set()

    monkeypatch.setattr(rounds, "in_progress_topics", fake_open)


def sign_in():
    app.dependency_overrides[current_user] = lambda: User(
        uid="member", email="member@example.com", email_verified=True, name="Ann"
    )


def no_certificates(monkeypatch):
    async def fake_certs(user_id, preparation_id):
        return {}

    monkeypatch.setattr(certificates, "for_preparation", fake_certs)


def fake_progress(monkeypatch, found):
    async def topic_progress(user_id, preparation_id):
        assert (user_id, preparation_id) == ("member", PREPARATION_ID)

        return found

    monkeypatch.setattr("app.routers.preparations.topic_progress", topic_progress)


def test_lists_answered_and_score_per_topic(client, monkeypatch):
    fake_progress(monkeypatch, {TOPIC_ID: (7, 86)})
    no_certificates(monkeypatch)
    sign_in()

    response = client.get(f"/preparations/{PREPARATION_ID}/progress")

    assert response.status_code == 200
    assert response.json() == [
        {
            "topic_id": str(TOPIC_ID),
            "answered": 7,
            "score": 86,
            "certificate_id": None,
            "in_progress": False,
        }
    ]


def test_marks_a_topic_with_an_open_round_even_before_any_answer(client, monkeypatch):
    async def fake_open(user_id, preparation_id):
        assert (user_id, preparation_id) == ("member", PREPARATION_ID)

        return {TOPIC_ID}

    fake_progress(monkeypatch, {})
    no_certificates(monkeypatch)
    monkeypatch.setattr(rounds, "in_progress_topics", fake_open)
    sign_in()

    response = client.get(f"/preparations/{PREPARATION_ID}/progress")

    assert response.json() == [
        {
            "topic_id": str(TOPIC_ID),
            "answered": 0,
            "score": None,
            "certificate_id": None,
            "in_progress": True,
        }
    ]


def test_lists_empty_before_any_finished_round(client, monkeypatch):
    fake_progress(monkeypatch, {})
    no_certificates(monkeypatch)
    sign_in()

    response = client.get(f"/preparations/{PREPARATION_ID}/progress")

    assert response.status_code == 200
    assert response.json() == []


def test_includes_certificate_even_without_current_answers(client, monkeypatch):
    """A question re-generated after the certificate leaves the topic with fewer answers."""
    cert_id = uuid.uuid4()
    other_topic = uuid.uuid4()

    async def fake_certs(user_id, preparation_id):
        return {TOPIC_ID: cert_id, other_topic: cert_id}

    fake_progress(monkeypatch, {TOPIC_ID: (10, 90)})
    monkeypatch.setattr(certificates, "for_preparation", fake_certs)
    sign_in()

    response = client.get(f"/preparations/{PREPARATION_ID}/progress")
    rows = {row["topic_id"]: row for row in response.json()}

    assert rows[str(TOPIC_ID)] == {
        "topic_id": str(TOPIC_ID),
        "answered": 10,
        "score": 90,
        "certificate_id": str(cert_id),
        "in_progress": False,
    }
    assert rows[str(other_topic)]["answered"] == 0
    assert rows[str(other_topic)]["score"] is None


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
