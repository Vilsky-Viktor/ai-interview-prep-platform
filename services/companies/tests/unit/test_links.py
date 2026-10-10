import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from prepza_common.auth import current_user, optional_user
from prepza_common.user import User

from app.constants.invites import LINK_STARTS_PER_HOUR, LINK_STARTS_PER_IP_HOUR, InviteStatus
from app.integrations import billing
from app.main import app
from app.models.interviews import Interview
from app.routers import links
from app.schemas.invites import InviteStartOut
from app.storage import companies, interviews, invites

INTERVIEW = Interview(
    id=uuid.uuid4(),
    company_id=uuid.uuid4(),
    generation_id=None,
    set_id=uuid.uuid4(),
    question_seconds=60,
    link_token="abc",
)


@pytest.fixture
def linked(monkeypatch):
    """The link "abc" opens INTERVIEW; returns what was held and started, and a way to set the
    candidate's current status or make billing refuse."""
    state = {"status": None, "broke": False, "held": [], "started": [], "counts": {}}

    async def get_by_link(token):
        return INTERVIEW if token == "abc" else None

    async def status_of(_interview_id, _email):
        return state["status"]

    async def held(_interview_id, _email):
        return state["status"], None

    async def hold(company_id, key):
        if state["broke"]:
            raise HTTPException(402, "Not enough credits. Top up to continue.")

        state["held"].append(key)

    async def for_link(interview_id, email, hold_key=None):
        return SimpleNamespace(email=email, hold_key=hold_key)

    async def start(invite, interview, user_id):
        state["started"].append(invite)

        return InviteStartOut(sessions=[])

    monkeypatch.setattr(interviews, "get_by_link", get_by_link)
    monkeypatch.setattr(invites, "held", held)
    monkeypatch.setattr(invites, "status_of", status_of)
    monkeypatch.setattr(invites, "for_link", for_link)
    monkeypatch.setattr(billing, "hold_candidate", hold)

    async def hit(redis, key, limit, window):
        state["counts"][key] = state["counts"].get(key, 0) + 1

        if state["counts"][key] > limit:
            raise HTTPException(429, "Too many requests. Try again later.")

    monkeypatch.setattr(links, "start_sessions", start)
    monkeypatch.setattr(links, "hit", hit)
    app.dependency_overrides[current_user] = lambda: User(
        uid="cand", email="Cand@Example.com", email_verified=True
    )

    yield state

    app.dependency_overrides.clear()


def test_anyone_signed_in_starts_through_the_link_and_is_charged_like_an_invite(client, linked):
    assert client.post("/links/abc/start").status_code == 200
    # Set aside under the new invite's own key.
    (key,) = linked["held"]
    assert key.startswith(f"{INTERVIEW.id}:cand@example.com:")
    assert [invite.email for invite in linked["started"]] == ["Cand@Example.com"]


def test_a_new_invite_that_cant_be_saved_gives_its_credits_back(client, linked, monkeypatch):
    """Its interview was deleted meanwhile."""
    released = []

    async def gone(interview_id, email, hold_key=None):
        raise RuntimeError("interview deleted")

    async def release(key):
        released.append(key)

    monkeypatch.setattr(invites, "for_link", gone)
    monkeypatch.setattr(billing, "release_candidate", release)

    with pytest.raises(RuntimeError):
        client.post("/links/abc/start")

    assert released == linked["held"] and len(released) == 1


def test_coming_back_continues_without_charging_again(client, linked):
    linked["status"] = "in_process"

    client.post("/links/abc/start")

    assert linked["held"] == []
    assert len(linked["started"]) == 1


def test_one_attempt_each_and_a_closed_or_broke_link_says_so(client, linked):
    linked["status"] = "finished"
    assert client.post("/links/abc/start").status_code == 409

    linked["status"], linked["broke"] = None, True
    refused = client.post("/links/abc/start")
    assert refused.status_code == 409
    assert refused.json()["detail"] == "This interview isn't taking new candidates right now."

    assert client.post("/links/nope/start").status_code == 404
    assert linked["started"] == []


def test_an_unverified_email_cant_start(client, linked):
    app.dependency_overrides[current_user] = lambda: User(
        uid="x", email="x@example.com", email_verified=False
    )

    assert client.post("/links/abc/start").status_code == 403
    assert linked["held"] == []


def test_the_link_says_when_the_signed_in_person_already_finished(client, linked, monkeypatch):
    async def no_company(_company_id):
        return None

    async def title(_interview):
        return "Backend"

    monkeypatch.setattr(companies, "get", no_company)
    monkeypatch.setattr(links, "interview_title", title)
    linked["status"] = "finished"
    app.dependency_overrides[optional_user] = lambda: User(
        uid="cand", email="cand@example.com", email_verified=True
    )

    signed_in = client.get("/links/abc").json()
    app.dependency_overrides[optional_user] = lambda: None
    signed_out = client.get("/links/abc").json()

    assert signed_in["status"] == "finished"
    assert signed_out["status"] is None


def test_a_link_takes_a_limited_number_of_new_candidates_an_hour(client, linked):
    linked["counts"][f"rate:link-starts:{INTERVIEW.id}"] = LINK_STARTS_PER_HOUR

    assert client.post("/links/abc/start").status_code == 429
    assert linked["held"] == []


def test_one_address_starts_a_limited_number_of_new_candidates_an_hour(client, linked):
    for _ in range(LINK_STARTS_PER_IP_HOUR):
        assert client.post("/links/abc/start").status_code == 200

    assert client.post("/links/abc/start").status_code == 429
    assert len(linked["held"]) == LINK_STARTS_PER_IP_HOUR


def test_a_candidate_already_invited_is_never_held_back_by_the_limits(client, linked):
    linked["status"] = InviteStatus.IN_PROCESS
    linked["counts"][f"rate:link-starts:{INTERVIEW.id}"] = LINK_STARTS_PER_HOUR

    assert client.post("/links/abc/start").status_code == 200
    assert linked["counts"] == {f"rate:link-starts:{INTERVIEW.id}": LINK_STARTS_PER_HOUR}
