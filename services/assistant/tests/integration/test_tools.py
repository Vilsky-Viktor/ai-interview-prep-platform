"""The tools against the running stack's services, as a throwaway Auth emulator user."""

import os
import uuid

import httpx
import pytest

from app.services.tool_calls import call_tool


@pytest.fixture
def token():
    """A new emulator user's ID token; the user is deleted after the test."""
    auth = f"http://{os.environ['FIREBASE_AUTH_EMULATOR_HOST']}/identitytoolkit.googleapis.com/v1"
    email = f"assistant-{uuid.uuid4().hex[:8]}@example.com"
    user = httpx.post(
        f"{auth}/accounts:signUp?key=demo",
        json={"email": email, "password": "secret123", "returnSecureToken": True},
    ).json()

    yield user["idToken"]

    httpx.post(
        f"{auth}/projects/{os.environ['FIREBASE_PROJECT_ID']}/accounts:delete",
        json={"localId": user["localId"]},
        headers={"Authorization": "Bearer owner"},
    )


def test_a_tool_calls_companies_as_the_user(run, token):
    companies = run(call_tool("list_companies", {}, token, "en", None))
    pause = run(call_tool("get_pause", {}, token, "en", None))

    # A new user has no companies yet.
    assert (companies.status_code, companies.content) == (
        200,
        {"data": [], "source": "list_companies"},
    )
    assert pause.content["data"] == {"paused": False}


def test_another_companys_data_is_refused_by_companies(run, token):
    result = run(call_tool("get_company", {"company_id": str(uuid.uuid4())}, token, "de", None))

    assert result.status_code in (403, 404)
    assert result.content["error"] == result.status_code
    assert result.content["detail"]


def test_a_forged_token_is_refused_downstream(run):
    result = run(call_tool("list_companies", {}, "forged", "en", None))

    assert result.status_code == 401
