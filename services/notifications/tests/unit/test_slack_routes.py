import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import pytest
from prepza_common.auth import current_user
from prepza_common.encryption import encrypt
from prepza_common.user import User

from app.config.settings import settings
from app.helpers.slack import signed_state
from app.integrations import companies
from app.integrations import slack as slack_api
from app.main import app
from app.storage import slack as storage

KEY = "Zm9vYmFyYmF6cXV4cXV1eGNvcmdlZ3JhdWx0Z2FycGw="


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    """Slack set up on the server, and Ann signed in as an owner of c1."""
    monkeypatch.setattr(settings, "slack_client_id", "client")
    monkeypatch.setattr(settings, "slack_client_secret", "secret")
    monkeypatch.setattr(settings, "slack_encryption_key", KEY)
    app.dependency_overrides[current_user] = lambda: User(
        uid="u1", email="u1@example.com", email_verified=True, name="Ann"
    )
    yield
    app.dependency_overrides.clear()


def member(monkeypatch, editor: bool, is_member: bool = True):
    async def access(company_id, user_id):
        return {"member": is_member, "editor": editor}

    monkeypatch.setattr(companies, "access", access)


def test_add_to_slack_goes_to_slacks_page_with_a_signed_state(client, monkeypatch):
    member(monkeypatch, editor=True)
    url = client.get("/slack/start?company_id=c1").json()["url"]
    query = parse_qs(urlparse(url).query)

    assert url.startswith("https://slack.com/oauth/v2/authorize?")
    assert query["scope"] == ["incoming-webhook"]
    assert query["redirect_uri"] == ["http://localhost:8090/api/notifications/slack/callback"]


def test_a_viewer_cant_add_slack_and_a_stranger_doesnt_see_the_company(client, monkeypatch):
    member(monkeypatch, editor=False)

    assert client.get("/slack/start?company_id=c1").status_code == 403
    assert client.delete("/slack?company_id=c1").status_code == 403

    member(monkeypatch, editor=False, is_member=False)

    assert client.get("/slack?company_id=c1").status_code == 404


def test_slack_not_set_up_on_the_server_says_so(client, monkeypatch):
    member(monkeypatch, editor=True)
    monkeypatch.setattr(settings, "slack_client_id", "")
    response = client.get("/slack/start?company_id=c1")

    assert response.status_code == 503
    assert response.json()["detail"] == "Slack isn't set up yet"


def state(expires_in=60):
    return signed_state(settings.service_secret, "c1", "u1", int(time.time()) + expires_in)


@pytest.fixture
def saved(monkeypatch):
    """What the callback saves and which earlier apps it removes; c1 had no channel before."""
    found = {"saved": None, "revoked": [], "earlier": None}

    async def get(company_id):
        return found["earlier"]

    async def connect(*args):
        found["saved"] = args

    async def revoke(token):
        found["revoked"].append(token)

    monkeypatch.setattr(storage, "get", get)
    monkeypatch.setattr(storage, "connect", connect)
    monkeypatch.setattr(slack_api, "revoke", revoke)

    return found


def callback(client, query):
    return client.get(f"/slack/callback?{query}", follow_redirects=False)


def test_back_from_slack_the_channel_is_saved_sealed_with_the_default_kinds(
    client, monkeypatch, saved
):
    async def exchange(code):
        return {"team": "Acme", "channel": "#hiring", "url": "https://hooks/x", "token": "t"}

    monkeypatch.setattr(slack_api, "exchange", exchange)
    response = callback(client, f"code=ok&state={state()}")
    company_id, team, channel, webhook, token, kinds, user_id = saved["saved"]

    assert response.status_code == 303
    assert response.headers["location"].endswith("/companies/c1/integrations/slack?slack=connected")
    assert (company_id, team, channel, user_id) == ("c1", "Acme", "#hiring", "u1")
    assert "https://hooks/x" not in webhook and token != "t"
    assert "candidate_finished" in kinds and "interview_ready" not in kinds


def test_reconnecting_keeps_the_kinds_and_removes_the_earlier_app(client, monkeypatch, saved):
    async def exchange(code):
        return {"team": "Acme", "channel": "#new", "url": "https://hooks/y", "token": "t2"}

    saved["earlier"] = SimpleNamespace(kinds=["interview_ready"], token=encrypt(KEY, "t1"))
    monkeypatch.setattr(slack_api, "exchange", exchange)
    callback(client, f"code=ok&state={state()}")

    assert saved["saved"][5] == ["interview_ready"]
    assert saved["revoked"] == ["t1"]


def test_cancelled_refused_and_expired_trips(client, monkeypatch, saved):
    async def refused(code):
        raise slack_api.SlackRefused("invalid_code")

    monkeypatch.setattr(slack_api, "exchange", refused)

    assert (
        callback(client, f"error=access_denied&state={state()}")
        .headers["location"]
        .endswith("?slack=cancelled")
    )
    assert (
        callback(client, f"code=bad&state={state()}").headers["location"].endswith("?slack=failed")
    )
    assert callback(client, f"code=ok&state={state(-1)}").status_code == 400
    assert saved["saved"] is None


def test_only_known_kinds_are_saved(client, monkeypatch):
    member(monkeypatch, editor=True)
    chosen = []

    async def get(company_id):
        return SimpleNamespace()

    async def set_kinds(company_id, kinds):
        chosen.append(kinds)

    monkeypatch.setattr(storage, "get", get)
    monkeypatch.setattr(storage, "set_kinds", set_kinds)
    body = {"kinds": ["interview_ready", "made_up", "candidate_finished"]}

    assert client.put("/slack/kinds?company_id=c1", json=body).status_code == 204
    assert chosen == [["candidate_finished", "interview_ready"]]
