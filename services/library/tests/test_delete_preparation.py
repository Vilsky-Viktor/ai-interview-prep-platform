import uuid

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.sets import SetKind, Visibility
from app.integrations import rounds
from app.main import app
from app.models.sets import QuestionSet
from app.storage import preparations

SET_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def setup(monkeypatch, kind=SetKind.PREPARATION):
    """Records deletes in the order they happen."""
    calls = []

    async def fake_get(set_id):
        return QuestionSet(
            id=SET_ID, kind=kind, owner_id="owner", visibility=Visibility.PUBLIC, title="T"
        )

    async def fake_remove(set_id):
        calls.append(("library", set_id))

    async def fake_rounds_delete(set_id):
        calls.append(("rounds", set_id))

    monkeypatch.setattr(preparations, "get", fake_get)
    monkeypatch.setattr(preparations, "remove", fake_remove)
    monkeypatch.setattr(rounds, "delete_preparation_data", fake_rounds_delete)

    return calls


def sign_in(uid):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=f"{uid}@example.com", email_verified=True
    )


def test_owner_deletes_preparation_and_its_practice_data_first(client, monkeypatch):
    calls = setup(monkeypatch)
    sign_in("owner")

    assert client.delete(f"/preparations/{SET_ID}").status_code == 204
    assert calls == [("rounds", SET_ID), ("library", SET_ID)]


def test_preparation_stays_when_rounds_cannot_delete(client, monkeypatch):
    calls = setup(monkeypatch)
    sign_in("owner")

    async def failing_rounds_delete(set_id):
        raise RuntimeError("rounds is down")

    monkeypatch.setattr(rounds, "delete_preparation_data", failing_rounds_delete)

    with pytest.raises(RuntimeError):
        client.delete(f"/preparations/{SET_ID}")

    assert calls == []


def test_anyone_else_gets_not_found(client, monkeypatch):
    calls = setup(monkeypatch)
    sign_in("member")

    assert client.delete(f"/preparations/{SET_ID}").status_code == 404
    assert calls == []


def test_company_interviews_are_not_deleted_here(client, monkeypatch):
    calls = setup(monkeypatch, kind=SetKind.INTERVIEW)
    sign_in("owner")

    assert client.delete(f"/preparations/{SET_ID}").status_code == 404
    assert calls == []
