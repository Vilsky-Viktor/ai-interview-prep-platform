import asyncio
import base64
import hashlib
import hmac
import json
import time

import httpx
import pytest
from fastapi import HTTPException
from prepza_common import http

from app.constants.ats import (
    TEAMTAILOR_API_VERSION,
    TEAMTAILOR_HOSTS,
    TEAMTAILOR_MEDIA_TYPE,
    TEAMTAILOR_PAGE,
)
from app.helpers.ats import teamtailor_signed
from app.integrations import ats_clients, teamtailor
from app.integrations.errors import KeyRejected

HOST = TEAMTAILOR_HOSTS[0]
NEXT = HOST + "/v1/jobs?page%5Bnumber%5D=2&page%5Bsize%5D=30"


@pytest.fixture
def api(monkeypatch):
    """Teamtailor, replaced: `answers` by (host, path) or path (a status, a json body, or a
    function of the request), every request recorded."""
    state = {"answers": {}, "requests": []}

    def handler(request):
        state["requests"].append(request)
        host = f"{request.url.scheme}://{request.url.host}"
        answers = state["answers"]
        answer = answers.get((host, request.url.path), answers.get(request.url.path, {}))

        if callable(answer):
            answer = answer(request)

        if isinstance(answer, int):
            return httpx.Response(answer)

        return httpx.Response(200, json=answer)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(http, "get_client", lambda: client)

    return state


def item(item_id, **attributes) -> dict:
    return {"id": item_id, "attributes": attributes}


def test_calls_carry_the_key_the_api_version_and_the_json_api_type(api):
    asyncio.run(teamtailor.check(HOST, "secret-key"))

    [request] = api["requests"]
    assert str(request.url) == HOST + "/v1/users?page%5Bsize%5D=1"
    assert request.headers["authorization"] == "Token token=secret-key"
    assert request.headers["x-api-version"] == TEAMTAILOR_API_VERSION
    assert request.headers["accept"] == TEAMTAILOR_MEDIA_TYPE
    assert request.headers["content-type"] == TEAMTAILOR_MEDIA_TYPE


@pytest.mark.parametrize("refusal", [401, 403])
def test_a_refused_key_is_a_rejected_key(api, refusal):
    api["answers"]["/v1/users"] = refusal

    with pytest.raises(KeyRejected):
        asyncio.run(teamtailor.check(HOST, "bad"))


def test_a_failing_or_unreachable_teamtailor_is_a_502(api):
    api["answers"]["/v1/users"] = 500

    with pytest.raises(HTTPException) as failed:
        asyncio.run(teamtailor.check(HOST, "key"))

    assert failed.value.status_code == 502

    def unreachable(request):
        raise httpx.ConnectError("down")

    api["answers"]["/v1/users"] = unreachable

    with pytest.raises(HTTPException) as failed:
        asyncio.run(teamtailor.check(HOST, "key"))

    assert failed.value.status_code == 502


def test_the_region_is_the_first_api_that_accepts_the_key(api):
    api["answers"][(HOST, "/v1/company")] = 401
    api["answers"][(TEAMTAILOR_HOSTS[1], "/v1/company")] = {
        "data": {"attributes": {"name": "Acme"}}
    }

    assert asyncio.run(teamtailor.region("key")) == (TEAMTAILOR_HOSTS[1], "Acme")
    assert len(api["requests"]) == 2


def test_a_key_no_region_accepts_is_rejected(api):
    api["answers"]["/v1/company"] = 401

    with pytest.raises(KeyRejected):
        asyncio.run(teamtailor.region("key"))

    assert len(api["requests"]) == len(TEAMTAILOR_HOSTS)


def test_jobs_are_read_page_by_page_and_archived_ones_left_out(api):
    def jobs(request):
        if "page[number]" in request.url.params:
            return {"data": [item(3, title="Support", status="open")]}

        assert request.url.params["page[size]"] == str(TEAMTAILOR_PAGE)

        return {
            "data": [item(1, title="Accountant", status="open"), item(2, status="archived")],
            "links": {"next": NEXT},
        }

    api["answers"]["/v1/jobs"] = jobs

    assert asyncio.run(teamtailor.jobs(HOST, "key")) == [
        {"id": "1", "name": "Accountant"},
        {"id": "3", "name": "Support"},
    ]
    # The next page is read at its own address, its query unchanged.
    assert str(api["requests"][1].url) == NEXT


def test_stages_come_in_their_order(api):
    api["answers"]["/v1/jobs/1/stages"] = {
        "data": [
            item(8, name="Offer", **{"row-order": 3}),
            item(6, name="Inbox", **{"row-order": 1}),
            item(7, name="Test", **{"row-order": 2}),
        ]
    }

    assert asyncio.run(teamtailor.stages(HOST, "key", "1")) == [
        {"id": "6", "name": "Inbox"},
        {"id": "7", "name": "Test"},
        {"id": "8", "name": "Offer"},
    ]


def test_a_job_is_its_title_pitch_and_body(api):
    api["answers"]["/v1/jobs/1"] = {
        "data": item(1, title="Accountant", pitch="<p>Join</p>", body=None)
    }

    assert asyncio.run(teamtailor.job(HOST, "key", "1")) == {
        "name": "Accountant",
        "sections": ["<p>Join</p>", ""],
    }


def test_an_application_is_its_job_stage_and_candidate_with_their_email(api):
    api["answers"]["/v1/job-applications/55"] = {
        "data": {
            "id": "55",
            "relationships": {
                "job": {"data": {"type": "jobs", "id": 101}},
                "stage": {"data": {"type": "stages", "id": "7"}},
                "candidate": {"data": {"type": "candidates", "id": "44"}},
            },
        },
        "included": [
            {"type": "jobs", "id": "101", "attributes": {"email": "no@x.com"}},
            {"type": "candidates", "id": "44", "attributes": {"email": "ann@example.com"}},
        ],
    }

    assert asyncio.run(teamtailor.application(HOST, "key", "55")) == {
        "job_id": "101",
        "stage_id": "7",
        "candidate_id": "44",
        "email": "ann@example.com",
    }
    assert api["requests"][0].url.params["include"] == "candidate"


def test_an_application_without_relationships_has_nothing(api):
    api["answers"]["/v1/job-applications/55"] = {"data": {"id": "55"}}

    assert asyncio.run(teamtailor.application(HOST, "key", "55")) == {
        "job_id": None,
        "stage_id": None,
        "candidate_id": None,
        "email": None,
    }


def users(by_email, everyone):
    def answer(request):
        if "filter[email]" in request.url.params:
            assert request.url.params["filter[email]"] == "ann@example.com"

            return {"data": by_email}

        return {"data": everyone}

    return answer


@pytest.mark.parametrize(
    ("by_email", "everyone", "chosen"),
    [
        ([item(5, role="user")], [], "5"),
        ([], [item(1, role="user"), item(2, role="admin"), item(3, role="admin")], "2"),
        ([], [item(1, role="user"), item(4, role="user")], "1"),
        ([], [], None),
    ],
)
def test_results_are_written_as_who_connected_else_an_admin_else_any_user(
    api, by_email, everyone, chosen
):
    api["answers"]["/v1/users"] = users(by_email, everyone)

    assert asyncio.run(teamtailor.member_id(HOST, "key", "ann@example.com")) == chosen


def test_a_note_goes_on_the_candidate_as_the_user(api):
    asyncio.run(teamtailor.comment(HOST, "key", "44", "5", "Grade: 82%"))

    [note] = api["requests"]
    assert (note.method, note.url.path) == ("POST", "/v1/notes")
    assert json.loads(note.content) == {
        "data": {
            "type": "notes",
            "attributes": {"note": "Grade: 82%"},
            "relationships": {
                "candidate": {"data": {"type": "candidates", "id": "44"}},
                "user": {"data": {"type": "users", "id": "5"}},
            },
        }
    }


def signature(secret: str, body: bytes, timestamp: str | None = None) -> str:
    timestamp = timestamp or str(int(time.time()))
    signed = timestamp.encode() + b"." + body
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()

    return base64.b64encode(f"t={timestamp},v2={digest}".encode()).decode()


def test_only_bodies_signed_with_the_signature_key_count():
    body = b'{"event_name": "job_application.update"}'
    given = signature("secret", body)

    assert teamtailor_signed("secret", body, given)
    assert not teamtailor_signed("other", body, given)
    assert not teamtailor_signed("secret", body + b" ", given)


@pytest.mark.parametrize("age", [301, -301, 3600])
def test_a_signature_older_than_five_minutes_or_from_the_future_doesnt_count(age):
    body = b'{"event_name": "job_application.update"}'

    assert teamtailor_signed("secret", body, signature("secret", body, str(int(time.time()) - 290)))
    assert not teamtailor_signed(
        "secret", body, signature("secret", body, str(int(time.time()) - age))
    )


def test_too_many_calls_are_answered_429_not_as_a_failure(api):
    api["answers"]["/v1/job-applications/55"] = 429

    with pytest.raises(HTTPException) as busy:
        asyncio.run(teamtailor.application(HOST, "k", "55"))

    assert busy.value.status_code == 429


@pytest.mark.parametrize(
    "given",
    [
        "",
        "not base64!",
        base64.b64encode(b"\xff\xfe").decode(),
        base64.b64encode(b"t=1").decode(),
        base64.b64encode(b"v2=abc").decode(),
        base64.b64encode(b"t=soon,v2=abc").decode(),
    ],
)
def test_a_broken_or_incomplete_signature_counts_as_unsigned(given):
    assert not teamtailor_signed("secret", b"{}", given)


def test_teamtailor_has_its_client():
    assert ats_clients.client("teamtailor") is teamtailor
    assert teamtailor.KEYS == ("host", "key")


def test_a_job_deleted_in_teamtailor_is_a_404_not_a_failure(api):
    api["answers"]["/v1/jobs/101"] = 404

    with pytest.raises(HTTPException) as gone:
        asyncio.run(teamtailor.job(HOST, "key", "101"))

    assert gone.value.status_code == 404
