import uuid
from types import SimpleNamespace

import pytest
from prepza_common.auth import current_user
from prepza_common.translations import TRANSLATIONS
from prepza_common.user import User

from app.constants.invites import (
    INTERVIEWS_PER_DAY,
    INTERVIEWS_PER_DAY_UNPAID,
    TOO_MANY_INTERVIEWS,
    TOO_MANY_INTERVIEWS_UNPAID,
    TOO_MANY_WITHOUT_CANDIDATES,
    TOO_MANY_WITHOUT_CANDIDATES_UNPAID,
)
from app.main import app
from app.routers import interviews as route
from app.services import interview_creation as creation
from app.storage import interviews

COMPANY_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def signed_in_manager(monkeypatch):
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True, name="Bob"
    )

    async def fake_company(user, company_id):
        return SimpleNamespace(id=COMPANY_ID), "owner"

    async def no_track(*args, **kwargs):
        return None

    monkeypatch.setattr(route, "require_editor", fake_company)
    monkeypatch.setattr(creation, "track", no_track)
    yield
    app.dependency_overrides.clear()


def generate(client, monkeypatch, waiting, paid=False):
    """Asks for a new interview while `waiting` generated interviews have no candidate, for a
    company that topped up (`paid`) or not; returns the response and the day's limit and
    generation it reached."""
    reached = []

    async def fake_waiting(company_id):
        return waiting

    async def fake_hit(redis, key, limit, window, message):
        reached.append(("day limit", limit, message))

    async def fake_generation(*args):
        reached.append(("generation", args[-1]))

        return {"id": str(uuid.uuid4()), "language": "en"}

    async def fake_paid(company_id):
        return paid

    async def fake_create(company_id, generation_id, language):
        return SimpleNamespace(id=uuid.uuid4())

    async def fake_out(interview):
        return {
            "id": str(interview.id),
            "generation_id": str(uuid.uuid4()),
            "set_id": None,
            "generation_failed": False,
            "title": None,
            "question_seconds": 60,
            "candidate_count": 0,
            "hired": False,
            "pass_mark": 70,
            "link_token": None,
            "status": "new",
            "created_at": "2026-10-04T09:00:00Z",
        }

    monkeypatch.setattr(interviews, "without_candidates", fake_waiting)
    monkeypatch.setattr(creation, "hit", fake_hit)
    monkeypatch.setattr(creation.generation_api, "create", fake_generation)
    monkeypatch.setattr(creation.billing, "company_paid", fake_paid)
    monkeypatch.setattr(interviews, "create", fake_create)
    monkeypatch.setattr(creation, "interview_out", fake_out)
    response = client.post(
        f"/interviews?company_id={COMPANY_ID}", json={"text": "Senior accountant job description"}
    )

    return response, reached


def test_an_unpaid_company_generates_another_only_once_its_one_waiting_has_a_candidate(
    client, monkeypatch
):
    response, reached = generate(client, monkeypatch, waiting=1)

    assert response.status_code == 429
    assert response.json()["detail"] == TOO_MANY_WITHOUT_CANDIDATES_UNPAID
    # Refused before the day's limit, so the attempt doesn't use one of the day's.
    assert reached == []


def test_a_paid_company_can_have_five_waiting(client, monkeypatch):
    allowed, _ = generate(client, monkeypatch, waiting=4, paid=True)
    refused, _ = generate(client, monkeypatch, waiting=5, paid=True)

    assert allowed.status_code == 201
    assert refused.status_code == 429
    assert refused.json()["detail"] == TOO_MANY_WITHOUT_CANDIDATES


def test_the_days_limit_is_three_until_the_first_top_up_and_ten_after(client, monkeypatch):
    _, unpaid = generate(client, monkeypatch, waiting=0)
    _, paid = generate(client, monkeypatch, waiting=0, paid=True)

    # An unpaid company's generation is sent as such, so the daily limit for everyone applies.
    assert unpaid == [
        ("day limit", INTERVIEWS_PER_DAY_UNPAID, TOO_MANY_INTERVIEWS_UNPAID),
        ("generation", False),
    ]
    assert paid == [("day limit", INTERVIEWS_PER_DAY, TOO_MANY_INTERVIEWS), ("generation", True)]


def test_the_limit_messages_have_translations():
    for language in TRANSLATIONS.values():
        for message in (
            TOO_MANY_WITHOUT_CANDIDATES,
            TOO_MANY_WITHOUT_CANDIDATES_UNPAID,
            TOO_MANY_INTERVIEWS_UNPAID,
        ):
            assert message in language
