import uuid

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.sets import SetKind, Visibility
from app.main import app
from app.models.sets import QuestionSet
from app.storage import preparations

SET_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def sign_in(uid):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=f"{uid}@example.com", email_verified=True, name="Ann"
    )


def question_set(owner_id):
    return QuestionSet(
        id=SET_ID,
        kind=SetKind.PREPARATION,
        owner_id=owner_id,
        visibility=Visibility.PRIVATE,
        title="Old",
    )


def test_owner_renames_preparation(client, monkeypatch):
    saved = []

    async def fake_get(set_id):
        return question_set("owner")

    async def fake_set_title(set_id, title):
        saved.append(title)

    monkeypatch.setattr(preparations, "get", fake_get)
    monkeypatch.setattr(preparations, "set_title", fake_set_title)
    sign_in("owner")
    response = client.patch(f"/preparations/{SET_ID}/title", json={"title": "  New name  "})

    assert response.status_code == 204
    assert saved == ["New name"]


def test_member_cannot_rename_preparation(client, monkeypatch):
    async def fake_get(set_id):
        return question_set("owner")

    monkeypatch.setattr(preparations, "get", fake_get)
    sign_in("member")

    assert (
        client.patch(f"/preparations/{SET_ID}/title", json={"title": "New name"}).status_code == 404
    )
