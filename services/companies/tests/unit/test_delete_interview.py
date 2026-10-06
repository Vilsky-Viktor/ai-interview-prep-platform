import uuid
from datetime import UTC, datetime

import httpx
import pytest
from prepza_common.auth import current_user
from prepza_common.user import User

from app.integrations import billing, library, rounds
from app.main import app
from app.models.companies import Company, Member
from app.models.interviews import Interview
from app.storage import companies, interviews, invites

COMPANY_ID = uuid.uuid4()
INTERVIEW_ID = uuid.uuid4()
SET_ID = uuid.uuid4()
URL = f"/interviews/{INTERVIEW_ID}"


def setup(monkeypatch, role, set_id=SET_ID):
    """Records the delete calls in order; bob has the given role."""
    calls = []
    interview = Interview(
        id=INTERVIEW_ID,
        company_id=COMPANY_ID,
        generation_id=uuid.uuid4(),
        set_id=set_id,
    )
    company = Company(id=COMPANY_ID, name="Acme", created_at=datetime.now(UTC))
    company.members = [
        Member(company_id=COMPANY_ID, user_id="bob", invited_email="bob@example.com", role=role),
    ]

    async def fake_interview(_interview_id):
        return interview

    async def fake_company(_company_id):
        return company

    async def fake_rounds(found_set_id):
        calls.append(("rounds", found_set_id))

    async def fake_library(found_set_id):
        calls.append(("library", found_set_id))

    async def fake_remove(interview_id):
        calls.append(("interview", interview_id))

    monkeypatch.setattr(interviews, "get", fake_interview)
    monkeypatch.setattr(companies, "get", fake_company)
    monkeypatch.setattr(rounds, "delete_interview_data", fake_rounds)
    monkeypatch.setattr(library, "delete_interview", fake_library)
    monkeypatch.setattr(interviews, "remove", fake_remove)
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True, name="bob"
    )

    return calls


def test_deletes_results_then_questions_then_the_interview(client, monkeypatch):
    calls = setup(monkeypatch, "admin")

    assert client.delete(URL).status_code == 204
    assert calls == [("rounds", SET_ID), ("library", SET_ID), ("interview", INTERVIEW_ID)]

    app.dependency_overrides.clear()


def test_viewers_cannot_delete(client, monkeypatch):
    calls = setup(monkeypatch, "viewer")

    assert client.delete(URL).status_code == 403
    assert calls == []

    app.dependency_overrides.clear()


def test_an_interview_still_generating_is_cancelled_instead(client, monkeypatch):
    calls = setup(monkeypatch, "admin", set_id=None)

    async def no_generation(_generation_id, _company_id):
        return None

    monkeypatch.setattr("app.helpers.interviews.generation_api.get", no_generation)

    assert client.delete(URL).status_code == 409
    assert calls == []

    app.dependency_overrides.clear()


def test_a_failed_cleanup_keeps_the_interview(client, monkeypatch):
    calls = setup(monkeypatch, "admin")

    async def failing_rounds(_set_id):
        request = httpx.Request("DELETE", "http://rounds")

        raise httpx.HTTPStatusError("down", request=request, response=httpx.Response(503))

    monkeypatch.setattr(rounds, "delete_interview_data", failing_rounds)

    with pytest.raises(httpx.HTTPStatusError):
        client.delete(URL)

    assert calls == []

    app.dependency_overrides.clear()


def test_deleting_an_interview_gives_back_unfinished_candidates_credits(client, monkeypatch):
    setup(monkeypatch, "admin")
    released = []

    async def unfinished(interview_id):
        return [(INTERVIEW_ID, "carol@example.com", "invited")]

    async def release(key):
        released.append(key)

    monkeypatch.setattr(invites, "unfinished", unfinished)
    monkeypatch.setattr(billing, "release_candidate", release)

    assert client.delete(URL).status_code == 204
    assert released == [f"{INTERVIEW_ID}:carol@example.com"]

    app.dependency_overrides.clear()
