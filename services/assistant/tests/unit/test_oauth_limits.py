import asyncio

import pytest
from fastapi import HTTPException
from mcp.server.auth.provider import AuthorizeError

from app.constants.limits import MAX_STATE_LENGTH
from app.routers import oauth as oauth_router
from app.services.oauth_provider import Provider
from app.storage import oauth
from tests.unit.test_oauth_provider import CLIENT, params


@pytest.fixture
def counted(monkeypatch):
    """The limits counted, without Redis; nothing is over them."""
    keys = []

    async def hit(redis, key, limit, window):
        keys.append(key)

    monkeypatch.setattr(oauth_router, "hit", hit)

    return keys


def test_a_registration_too_large_to_keep_is_refused(client, counted, monkeypatch):
    saved = []

    async def save_client(client_id, info):
        saved.append(info)

    monkeypatch.setattr(oauth, "save_client", save_client)
    body = {"client_name": "x" * 5_000, "redirect_uris": ["http://localhost/cb"]}

    response = client.post("/register", json=body)

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_client_metadata"
    assert saved == []


def test_requests_to_connect_are_counted_per_address(client, counted, monkeypatch):
    async def unknown(client_id):
        return None

    monkeypatch.setattr(oauth, "get_client", unknown)
    query = {
        "client_id": "unknown",
        "response_type": "code",
        "code_challenge": "challenge",
        "redirect_uri": "https://claude.ai/api/mcp/auth_callback",
    }
    client.get("/authorize", params=query, follow_redirects=False)

    assert counted == ["rate:assistant:mcp:authorize:testclient"]


def test_too_many_requests_to_connect_from_one_address_are_refused(client, monkeypatch):
    async def over(redis, key, limit, window):
        raise HTTPException(429, "Too many requests. Try again later.")

    monkeypatch.setattr(oauth_router, "hit", over)

    response = client.get("/authorize", params={"client_id": "c1"}, follow_redirects=False)

    assert response.status_code == 429
    assert response.json()["error"] == "invalid_request"


def test_a_state_too_long_to_keep_is_refused():
    request = params().model_copy(update={"state": "s" * (MAX_STATE_LENGTH + 1)})

    with pytest.raises(AuthorizeError):
        asyncio.run(Provider().authorize(CLIENT, request))
