import httpx
import pytest

from app.integrations import billing
from app.routers import links
from app.storage import invites
from tests.unit.test_links import linked  # noqa: F401

URL = "/links/abc/start"


@pytest.fixture
def released(monkeypatch):
    """The credits given back; an invite the candidate already has keeps "stored-key"."""
    keys = []

    async def release(key):
        keys.append(key)

    monkeypatch.setattr(billing, "release_candidate", release)

    return keys


def with_stored_key(monkeypatch, linked):  # noqa: F811
    async def held(_interview_id, _email):
        return linked["status"], "stored-key" if linked["status"] else None

    monkeypatch.setattr(invites, "held", held)


def test_an_expired_invite_that_fails_to_start_gives_its_credits_back(
    client,
    linked,  # noqa: F811
    released,
    monkeypatch,
):
    """Expiry won't give them back again: it only releases invites that haven't expired."""
    linked["status"] = "expired"
    with_stored_key(monkeypatch, linked)

    async def rounds_down(invite, interview, user):
        raise httpx.ConnectError("rounds is down")

    monkeypatch.setattr(links, "start_sessions", rounds_down)

    with pytest.raises(httpx.HTTPError):
        client.post(URL)

    assert linked["held"] == ["stored-key"]
    assert released == ["stored-key"]


@pytest.mark.parametrize("status, given_back", [(None, True), ("invited", False)])
def test_a_lost_answer_from_billing_gives_back_only_a_hold_made_just_now(
    client,
    linked,  # noqa: F811
    released,
    monkeypatch,
    status,
    given_back,
):
    linked["status"] = status
    with_stored_key(monkeypatch, linked)

    async def lost(company_id, key):
        linked["held"].append(key)

        raise httpx.ReadTimeout("billing took too long")

    monkeypatch.setattr(billing, "hold_candidate", lost)

    with pytest.raises(httpx.HTTPError):
        client.post(URL)

    assert released == (linked["held"] if given_back else [])
