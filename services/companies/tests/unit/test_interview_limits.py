import uuid
from types import SimpleNamespace

import pytest
from prepza_common.auth import current_user
from prepza_common.translations import TRANSLATIONS
from prepza_common.user import User

from app.constants.invites import TOO_MANY_WITHOUT_CANDIDATES
from app.main import app
from app.routers import interviews as route
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

    monkeypatch.setattr(route, "require_company", fake_company)
    monkeypatch.setattr(route, "track", no_track)
    yield
    app.dependency_overrides.clear()


def generate(client, monkeypatch, waiting):
    """Asks for a new interview while `waiting` interviews have no candidate; returns the response
    and whether the day's counter and generation were reached."""
    reached = []

    async def fake_waiting(company_id):
        return waiting

    async def fake_hit(*args):
        reached.append("day limit")

    async def fake_generation(*args):
        reached.append("generation")

        return {"id": str(uuid.uuid4()), "language": "en"}

    async def fake_create(company_id, generation_id, language):
        return SimpleNamespace(id=uuid.uuid4())

    async def fake_out(interview):
        return {
            "id": str(interview.id),
            "generation_id": str(uuid.uuid4()),
            "set_id": None,
            "title": None,
            "question_seconds": 60,
            "candidate_count": 0,
            "created_at": "2026-10-04T09:00:00Z",
        }

    monkeypatch.setattr(interviews, "without_candidates", fake_waiting)
    monkeypatch.setattr(route, "hit", fake_hit)
    monkeypatch.setattr(route.generation_api, "create", fake_generation)
    monkeypatch.setattr(interviews, "create", fake_create)
    monkeypatch.setattr(route, "interview_out", fake_out)
    response = client.post(
        f"/interviews?company_id={COMPANY_ID}", json={"text": "Senior accountant job description"}
    )

    return response, reached


def test_three_interviews_waiting_without_candidates_stop_a_new_one(client, monkeypatch):
    response, reached = generate(client, monkeypatch, waiting=3)

    assert response.status_code == 429
    assert response.json()["detail"] == TOO_MANY_WITHOUT_CANDIDATES
    # Refused before the day's limit, so the attempt doesn't use one of the 10.
    assert reached == []


def test_fewer_waiting_interviews_let_a_new_one_be_generated(client, monkeypatch):
    _, reached = generate(client, monkeypatch, waiting=2)

    assert reached == ["day limit", "generation"]


def test_the_waiting_limit_message_has_translations():
    for language in TRANSLATIONS.values():
        assert TOO_MANY_WITHOUT_CANDIDATES in language
