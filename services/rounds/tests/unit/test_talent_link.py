from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.main import app
from app.storage import talents


@pytest.fixture
def stored(monkeypatch):
    """Ann signed in; the saved link lives in a dict."""
    app.dependency_overrides[current_user] = lambda: User(
        uid="ann", email="ann@example.com", email_verified=True, name="Ann Lee"
    )
    links = {}

    async def get(user_id):
        return links.get(user_id)

    async def save(user_id, name, url):
        links[user_id] = SimpleNamespace(name=name, url=url, decided_at=datetime.now(UTC))

        return links[user_id]

    monkeypatch.setattr(talents, "get", get)
    monkeypatch.setattr(talents, "save", save)

    yield links

    app.dependency_overrides.clear()


def test_a_talent_is_asked_once_shares_a_link_and_withdraws_it(client, stored):
    assert client.get("/talent-link").json() == {"decided": False, "url": None}

    saved = client.put("/talent-link", json={"url": "https://www.linkedin.com/in/ann-lee"})

    assert saved.json() == {"decided": True, "url": "https://www.linkedin.com/in/ann-lee"}
    assert stored["ann"].name == "Ann Lee"

    # No link withdraws, and still counts as answered: they aren't asked again.
    assert client.put("/talent-link", json={}).json() == {"decided": True, "url": None}


def test_declining_is_an_answer_too(client, stored):
    client.put("/talent-link", json={"url": None})

    assert client.get("/talent-link").json() == {"decided": True, "url": None}


def test_only_a_linkedin_link_is_accepted(client, stored):
    assert client.put("/talent-link", json={"url": "https://ann.dev"}).status_code == 422
    assert (
        client.put("/talent-link", json={"url": "https://linkedin.com.evil.io/in/a"}).status_code
        == 422
    )
    assert (
        client.put("/talent-link", json={"url": "https://uk.linkedin.com/in/ann"}).status_code
        == 200
    )


def test_only_a_web_address_is_accepted(client, stored):
    assert client.put("/talent-link", json={"url": "not a link"}).status_code == 422
    assert client.put("/talent-link", json={"url": "javascript:alert(1)"}).status_code == 422
    assert (
        client.put(
            "/talent-link", json={"url": "https://www.linkedin.com/in/" + "a" * 300}
        ).status_code
        == 422
    )
    assert stored == {}
