import uuid

import httpx
import pytest
from prepza_common.auth import current_user
from prepza_common.translations import TRANSLATIONS
from prepza_common.user import User

from app.constants.sets import SetKind, Visibility
from app.constants.titles import TITLE_CHECK_FAILED, TITLE_HAS_COMPANY
from app.integrations import generation
from app.main import app
from app.models.sets import QuestionSet
from app.services import titles
from app.storage import preparations

SET_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def signed_in_owner(monkeypatch):
    app.dependency_overrides[current_user] = lambda: User(
        uid="owner", email="owner@example.com", email_verified=True, name="Ann"
    )

    async def no_limit(*_args):
        return None

    monkeypatch.setattr(titles, "hit", no_limit)
    yield
    app.dependency_overrides.clear()


def kit(monkeypatch, visibility, title="Accountant at Acme"):
    """The owner's kit, with what was checked and saved recorded."""
    seen = {"checked": [], "visibility": [], "title": []}

    async def fake_get(_set_id):
        return QuestionSet(
            id=SET_ID,
            kind=SetKind.PREPARATION,
            owner_id="owner",
            visibility=visibility,
            title=title,
        )

    async def fake_check(checked):
        seen["checked"].append(checked)

        return "Acme" in checked

    async def save_visibility(_set_id, value):
        seen["visibility"].append(value)

    async def save_title(_set_id, value):
        seen["title"].append(value)

    monkeypatch.setattr(preparations, "get", fake_get)
    monkeypatch.setattr(generation, "title_has_company", fake_check)
    monkeypatch.setattr(preparations, "set_visibility", save_visibility)
    monkeypatch.setattr(preparations, "set_title", save_title)

    return seen


def test_a_title_naming_a_company_cant_go_public(client, monkeypatch):
    seen = kit(monkeypatch, Visibility.PRIVATE)

    response = client.patch(f"/preparations/{SET_ID}", json={"visibility": "public"})

    assert response.status_code == 422
    assert response.json()["detail"] == TITLE_HAS_COMPANY
    assert seen["checked"] == ["Accountant at Acme"]
    assert seen["visibility"] == []


def test_a_plain_title_goes_public_and_going_private_isnt_checked(client, monkeypatch):
    seen = kit(monkeypatch, Visibility.PRIVATE, title="Senior accountant")

    assert client.patch(f"/preparations/{SET_ID}", json={"visibility": "public"}).status_code == 204

    seen = kit(monkeypatch, Visibility.PUBLIC)

    assert (
        client.patch(f"/preparations/{SET_ID}", json={"visibility": "private"}).status_code == 204
    )
    assert seen["checked"] == []


def test_renaming_a_public_kit_is_checked_and_a_private_one_isnt(client, monkeypatch):
    seen = kit(monkeypatch, Visibility.PUBLIC, title="Accountant")
    url = f"/preparations/{SET_ID}/title"

    assert client.patch(url, json={"title": "Accountant at Acme"}).status_code == 422
    assert client.patch(url, json={"title": "Senior accountant"}).status_code == 204
    assert seen["title"] == ["Senior accountant"]

    seen = kit(monkeypatch, Visibility.PRIVATE, title="Accountant")

    assert client.patch(url, json={"title": "Accountant at Acme"}).status_code == 204
    assert seen["checked"] == []


def test_a_title_that_cant_be_checked_doesnt_go_public(client, monkeypatch):
    seen = kit(monkeypatch, Visibility.PRIVATE, title="Senior accountant")

    async def down(_title):
        raise httpx.ConnectError("generation is down")

    monkeypatch.setattr(generation, "title_has_company", down)

    response = client.patch(f"/preparations/{SET_ID}", json={"visibility": "public"})

    assert response.status_code == 503
    assert response.json()["detail"] == TITLE_CHECK_FAILED
    assert seen["visibility"] == []


def test_title_messages_have_translations():
    for language in TRANSLATIONS.values():
        assert TITLE_HAS_COMPANY in language
        assert TITLE_CHECK_FAILED in language
