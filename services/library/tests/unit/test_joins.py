import uuid

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.sets import SetKind, Visibility
from app.main import app
from app.models.sets import QuestionSet
from app.storage import feedback, joins, preparations

SET_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def sign_in(uid="member"):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=f"{uid}@example.com", email_verified=True, name="Ann"
    )


def question_set(visibility=Visibility.PUBLIC, owner_id="owner"):
    return QuestionSet(
        id=SET_ID, kind=SetKind.PREPARATION, owner_id=owner_id, visibility=visibility
    )


def test_public_user_can_join(client, monkeypatch):
    joined = []

    async def fake_get(set_id):
        return question_set()

    async def fake_is_joined(set_id, user_id):
        return False

    async def fake_join(set_id, user_id):
        joined.append(user_id)

    monkeypatch.setattr(preparations, "get", fake_get)
    monkeypatch.setattr(joins, "is_joined", fake_is_joined)
    monkeypatch.setattr(joins, "join", fake_join)
    sign_in()

    assert client.post(f"/preparations/{SET_ID}/join").status_code == 204
    assert joined == ["member"]


def test_private_stranger_cannot_join(client, monkeypatch):
    async def fake_get(set_id):
        return question_set(Visibility.PRIVATE)

    async def fake_is_joined(set_id, user_id):
        return False

    monkeypatch.setattr(preparations, "get", fake_get)
    monkeypatch.setattr(joins, "is_joined", fake_is_joined)
    sign_in("eve")

    assert client.post(f"/preparations/{SET_ID}/join").status_code == 404


def test_joined_user_can_rate(client, monkeypatch):
    rated = []

    async def fake_get(set_id):
        return question_set(Visibility.PRIVATE)

    async def fake_is_joined(set_id, user_id):
        return user_id == "member"

    async def fake_rate(set_id, user_id, value):
        rated.append((user_id, value))

    monkeypatch.setattr(preparations, "get", fake_get)
    monkeypatch.setattr(joins, "is_joined", fake_is_joined)
    monkeypatch.setattr(feedback, "rate_preparation", fake_rate)
    sign_in()

    response = client.put(f"/preparations/{SET_ID}/rating", json={"value": 5})
    again = client.put(f"/preparations/{SET_ID}/rating", json={"value": 1})

    assert response.status_code == 204
    assert again.status_code == 204
    assert rated == [("member", 5), ("member", 1)]


def test_owner_cannot_rate(client, monkeypatch):
    async def fake_get(set_id):
        return question_set()

    monkeypatch.setattr(preparations, "get", fake_get)
    sign_in("owner")

    response = client.put(f"/preparations/{SET_ID}/rating", json={"value": 5})

    assert response.status_code == 403


def test_owner_cannot_leave(client, monkeypatch):
    async def fake_get(set_id):
        return question_set()

    monkeypatch.setattr(preparations, "get", fake_get)
    sign_in("owner")

    assert client.delete(f"/preparations/{SET_ID}/join").status_code == 403
