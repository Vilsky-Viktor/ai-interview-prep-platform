import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.helpers.keys import hashed
from tests.unit.conftest import CANDIDATE, COMPANY, INTERVIEW

KEY = "pz_test-key"


@pytest.fixture
def key(stored):
    """A working key of COMPANY, made by u1 (an owner)."""
    row = type("Key", (), {})()
    row.id, row.company_id, row.created_by = uuid.uuid4(), COMPANY, "u1"
    row.hash, row.expires_at = hashed(KEY), None
    stored["keys"].append(row)

    return row


def call(client, method, path, key=KEY, **kwargs):
    headers = {"Authorization": f"Bearer {key}"} if key else {}

    return client.request(method, path, headers=headers, **kwargs)


def test_a_key_lists_its_companys_interviews_and_notes_its_use(client, companies_api, key, stored):
    response = call(client, "GET", "/interviews")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(INTERVIEW),
            "title": "Backend",
            "status": "in_process",
            "ready": True,
            "pass_mark": 70,
            "candidate_count": 1,
            "created_at": "2026-10-01T09:00:00Z",
        }
    ]
    assert stored["used"] == [key.id]


def test_a_candidate_comes_with_signals_and_a_link_to_their_results(client, companies_api, key):
    found = call(client, "GET", f"/interviews/{INTERVIEW}/candidates/{CANDIDATE}").json()

    assert found["signals"] == {"tab_leaves": 0, "copies": 1, "fast_answers": 0}
    assert found["results_url"] == (
        f"http://localhost:8090/companies/{COMPANY}/interviews/{INTERVIEW}/candidates/{CANDIDATE}"
    )
    assert "tab_leaves" not in found


def test_an_invite_goes_out_as_the_keys_creator(client, companies_api, key):
    response = call(
        client, "POST", f"/interviews/{INTERVIEW}/candidates", json={"email": "bob@example.com"}
    )

    assert response.status_code == 201
    assert companies_api["sent"] == [(INTERVIEW, "bob@example.com", "u1")]


@pytest.mark.parametrize("refusal", [402, 409, 429, 503])
def test_companies_refusals_pass_through(client, companies_api, key, refusal):
    companies_api["refuse"] = refusal
    response = call(
        client, "POST", f"/interviews/{INTERVIEW}/candidates", json={"email": "bob@example.com"}
    )

    assert response.status_code == refusal


def test_another_companys_interview_is_not_found(client, companies_api, key):
    other = uuid.uuid4()

    assert call(client, "GET", f"/interviews/{other}").status_code == 404
    assert (
        call(
            client, "POST", f"/interviews/{other}/candidates", json={"email": "b@example.com"}
        ).status_code
        == 404
    )
    assert companies_api["sent"] == []


@pytest.mark.parametrize("sent", [None, "pz_wrong", "not-even-a-key"])
def test_no_key_or_an_unknown_one_is_refused(client, companies_api, stored, sent):
    response = call(client, "GET", "/interviews", key=sent)

    assert response.status_code == 401
    assert stored["used"] == []


def test_an_expired_key_is_refused(client, companies_api, key):
    key.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    response = call(client, "GET", "/interviews")

    assert response.status_code == 401
    assert response.json()["detail"] == "This API key has expired"


@pytest.mark.parametrize("role", ["viewer", None])
def test_a_key_stops_working_once_its_creator_cant_edit(client, companies_api, key, role):
    companies_api["roles"]["u1"] = role

    assert call(client, "GET", "/interviews").status_code == 401


def test_over_the_rate_limit_is_refused(client, companies_api, key, stored):
    stored["limited"] = True

    assert call(client, "GET", "/interviews").status_code == 429


def test_the_public_reference_lists_only_the_public_api(client):
    spec = client.get("/openapi.json").json()

    assert set(spec["paths"]) == {
        "/interviews",
        "/interviews/{interview_id}",
        "/interviews/{interview_id}/candidates",
        "/interviews/{interview_id}/candidates/{candidate_id}",
    }
    assert list(spec["webhooks"]) == ["candidate.finished"]


def test_the_reference_says_results_must_not_reject_candidates_automatically(client):
    spec = client.get("/openapi.json").json()
    candidate = spec["components"]["schemas"]["Candidate"]["properties"]

    assert "don't reject candidates automatically" in spec["info"]["description"].lower()
    assert "reject a candidate automatically" in candidate["passed"]["description"]
    assert (
        "reject a candidate automatically"
        in spec["components"]["schemas"]["Signals"]["description"]
    )
