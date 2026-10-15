import uuid
from types import SimpleNamespace

import pytest

from app.constants.audit import VIA_API
from app.constants.invites import NO_EMAILS_FOR_GUEST
from app.routers import internal_api_changes
from app.services import candidate_changes, candidate_invites, credits
from app.storage import candidates, companies, interviews
from tests.unit.test_internal_api import COMPANY_ID, HEADERS, INTERVIEW, OTHER_ID

BASE = f"/internal/companies/{COMPANY_ID}"


@pytest.fixture
def world(monkeypatch):
    """The company's interview with one candidate (`state["invite"]`); returns what was done."""
    state = {
        "invite": SimpleNamespace(
            id=uuid.uuid4(), email="anna@example.com", status="invited", guest=False
        ),
        "done": [],
    }

    async def get_interview(interview_id):
        return INTERVIEW if interview_id == INTERVIEW.id else None

    async def get_candidate(interview_id, invite_id):
        invite = state["invite"]

        return invite if invite_id == invite.id else None

    async def get_company(company_id):
        return SimpleNamespace(id=company_id) if company_id == COMPANY_ID else None

    def record(name):
        async def done(*args, **kwargs):
            state["done"].append((name, *args))

        return done

    async def outbox():
        pass

    monkeypatch.setattr(interviews, "get", get_interview)
    monkeypatch.setattr(candidates, "get", get_candidate)
    monkeypatch.setattr(companies, "get", get_company)
    monkeypatch.setattr(candidate_changes, "remove", record("remove"))
    monkeypatch.setattr(candidate_invites, "invite", record("invite"))
    monkeypatch.setattr(internal_api_changes.outbox_service, "flush_quietly", outbox)

    return state


def candidate_path(state, company_id=COMPANY_ID):
    return f"/internal/companies/{company_id}/interviews/{INTERVIEW.id}/candidates/{state['invite'].id}"


def test_a_candidate_is_removed_as_the_keys_creator_through_the_api(client, world):
    response = client.delete(candidate_path(world), params={"user_id": "ann"}, headers=HEADERS)
    other = client.delete(
        candidate_path(world, OTHER_ID), params={"user_id": "ann"}, headers=HEADERS
    )

    assert (response.status_code, other.status_code) == (204, 404)
    assert world["done"] == [("remove", INTERVIEW, world["invite"], "ann", VIA_API)]


def test_a_reminder_goes_out_again_but_not_to_a_guest(client, world):
    sent = client.post(
        f"{candidate_path(world)}/resend", params={"user_id": "ann"}, headers=HEADERS
    )
    world["invite"].guest = True
    guest = client.post(
        f"{candidate_path(world)}/resend", params={"user_id": "ann"}, headers=HEADERS
    )

    assert sent.status_code == 204
    assert (guest.status_code, guest.json()["detail"]) == (409, NO_EMAILS_FOR_GUEST)
    [(name, interview, _company, sender, email)] = world["done"]
    assert (name, interview, sender.uid, email) == ("invite", INTERVIEW, "ann", "anna@example.com")


def test_a_candidate_is_found_by_exact_email_and_credits_are_read(client, world, monkeypatch):
    asked = []

    async def company_page(company_id, offset, limit, q="", email=""):
        asked.append(email)

        return [(world["invite"], INTERVIEW)]

    async def credits_of(company_id):
        return {"available": 1500, "low": False}

    monkeypatch.setattr(candidates, "company_page", company_page)
    monkeypatch.setattr(credits, "credits_of", credits_of)

    found = client.get(f"{BASE}/candidates", params={"email": "anna@example.com"}, headers=HEADERS)
    balance = client.get(f"{BASE}/credits", headers=HEADERS)

    assert found.json() == [
        {"interview_id": str(INTERVIEW.id), "candidate_id": str(world["invite"].id)}
    ]
    assert asked == ["anna@example.com"]
    assert balance.json()["available"] == 1500


def test_the_api_routes_need_a_service_token(client, world):
    assert client.get(f"{BASE}/credits").status_code in (401, 403)
