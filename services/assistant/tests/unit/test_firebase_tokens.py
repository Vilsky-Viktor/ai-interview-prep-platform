import asyncio
from types import SimpleNamespace

import httpx
import pytest
from firebase_admin import auth as firebase_auth
from prepza_common import http, memory_cache
from prepza_common.user import User

from app.config.settings import settings
from app.integrations import firebase_tokens

ANN = User(uid="ann", email="ann@example.com", email_verified=True, language="de")


@pytest.fixture
def firebase(monkeypatch):
    """Firebase's accounts and sign-in API: every sign-in posted."""
    state = SimpleNamespace(accounts={"ann": False}, posts=[])

    def get_user(uid):
        if uid not in state.accounts:
            raise firebase_auth.UserNotFoundError("gone")

        return SimpleNamespace(disabled=state.accounts[uid])

    class Client:
        async def post(self, url, params, json):
            state.posts.append((url, params, json))
            request = httpx.Request("POST", url)

            return httpx.Response(
                200, json={"idToken": "id-token", "expiresIn": "3600"}, request=request
            )

    monkeypatch.setattr(firebase_auth, "get_user", get_user)
    monkeypatch.setattr(firebase_auth, "create_custom_token", lambda uid: b"custom")
    monkeypatch.setattr(http, "get_client", Client)
    monkeypatch.setattr(firebase_tokens, "verify", lambda token: ANN)
    firebase_tokens.forget("ann")

    yield state

    firebase_tokens.forget("ann")


def test_the_user_is_signed_in_with_a_custom_token_and_kept(firebase):
    first = asyncio.run(firebase_tokens.sign_in("ann"))
    again = asyncio.run(firebase_tokens.sign_in("ann"))

    assert first == again == (ANN, "id-token")
    [(url, params, body)] = firebase.posts
    assert url.endswith("/accounts:signInWithCustomToken")
    assert params == {"key": settings.firebase_web_api_key}
    assert body == {"token": "custom", "returnSecureToken": True}


def test_forgetting_signs_in_again(firebase):
    asyncio.run(firebase_tokens.sign_in("ann"))
    firebase_tokens.forget("ann")
    asyncio.run(firebase_tokens.sign_in("ann"))

    assert len(firebase.posts) == 2
    assert memory_cache.get("mcp:id-token:ann") == (ANN, "id-token")


@pytest.mark.parametrize("disabled", [None, True], ids=["deleted", "disabled"])
def test_an_account_thats_gone_or_disabled_isnt_signed_in(firebase, disabled):
    if disabled is None:
        firebase.accounts.clear()
    else:
        firebase.accounts["ann"] = True

    assert asyncio.run(firebase_tokens.sign_in("ann")) is None
    # Never a custom token for an unknown account: it would create one.
    assert firebase.posts == []


def test_the_emulator_is_used_locally_and_google_otherwise(monkeypatch):
    monkeypatch.setattr(settings, "firebase_auth_emulator_host", "firebase-auth:9199")
    local = firebase_tokens.identity_url()
    monkeypatch.setattr(settings, "firebase_auth_emulator_host", "")

    assert local == "http://firebase-auth:9199/identitytoolkit.googleapis.com/v1"
    assert firebase_tokens.identity_url() == "https://identitytoolkit.googleapis.com/v1"
