import asyncio
import json
import socket
import uuid
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException
from prepza_common.encryption import encrypt

from app.services import events
from app.services import webhooks as delivery
from tests.unit.conftest import CANDIDATE, COMPANY, INTERVIEW, KEY

FINISHED = {
    "candidate_invite_id": str(CANDIDATE),
    "interview_id": str(INTERVIEW),
    "company_id": str(COMPANY),
    "title": "Backend",
    "grade": 86,
    "passed": True,
    "flagged": True,
}


@pytest.fixture
def endpoints(monkeypatch, companies_api):
    """COMPANY's web hooks, what each endpoint got, which fail or don't resolve,
    and which got which event."""
    state = {
        "hooks": [],
        "posted": [],
        "failing": set(),
        "delivered": set(),
        "public": True,
        "unresolved": set(),
    }

    def hook(url, secret="whsec_a", maker="u1"):
        found = SimpleNamespace(
            id=uuid.uuid4(), url=url, secret=encrypt(KEY, secret), created_by=maker
        )
        state["hooks"].append(found)

        return found

    async def of_company(company_id):
        return state["hooks"] if company_id == COMPANY else []

    async def delivered(webhook_id, event_id):
        return (webhook_id, event_id) in state["delivered"]

    async def mark_delivered(webhook_id, event_id):
        state["delivered"].add((webhook_id, event_id))

    async def post(url, body, signature):
        if url in state["failing"]:
            raise httpx.ConnectError("down")

        state["posted"].append((url, json.loads(body), signature))

    monkeypatch.setattr(delivery.webhooks, "of_company", of_company)
    monkeypatch.setattr(delivery.webhooks, "delivered", delivered)
    monkeypatch.setattr(delivery.webhooks, "mark_delivered", mark_delivered)
    monkeypatch.setattr(delivery.endpoints, "post", post)
    monkeypatch.setattr(delivery, "public_address", lambda url: check(url, state))
    state["hook"] = hook

    return state


def check(url, state):
    """public_address, faked: an address in state["unresolved"] doesn't resolve."""
    if url in state["unresolved"]:
        raise socket.gaierror

    return state["public"]


def finish(event_id="e1"):
    asyncio.run(delivery.finished(FINISHED, event_id))


def test_each_web_hook_gets_the_interview_and_candidate_signed(endpoints):
    endpoints["hook"]("https://a.example/x")
    endpoints["hook"]("https://b.example/x")
    finish()
    (_, body, signature), _ = endpoints["posted"]

    assert sorted(item[0] for item in endpoints["posted"]) == [
        "https://a.example/x",
        "https://b.example/x",
    ]
    assert body["id"] == "e1" and body["type"] == "candidate.finished"
    assert body["data"]["interview"]["id"] == str(INTERVIEW)
    assert body["data"]["candidate"]["grade"] == 86
    assert signature.startswith("t=") and ",v1=" in signature


def test_a_redelivered_event_reaches_only_the_web_hooks_that_failed(endpoints):
    endpoints["hook"]("https://a.example/x")
    endpoints["hook"]("https://down.example/x")
    endpoints["failing"].add("https://down.example/x")

    # One failed: the event raises, so Pub/Sub sends it again.
    with pytest.raises(delivery.DeliveryFailed):
        finish()

    endpoints["failing"].clear()
    finish()

    assert [item[0] for item in endpoints["posted"]] == [
        "https://a.example/x",
        "https://down.example/x",
    ]
    finish()
    assert len(endpoints["posted"]) == 2


def test_a_web_hook_added_by_someone_no_longer_an_editor_gets_nothing(endpoints, companies_api):
    endpoints["hook"]("https://kept.example/x")
    endpoints["hook"]("https://left.example/x", maker="u2")
    companies_api["roles"]["u2"] = "viewer"

    finish()

    assert [item[0] for item in endpoints["posted"]] == ["https://kept.example/x"]


def test_without_web_hooks_companies_isnt_asked(endpoints, companies_api):
    companies_api["missing"] = True

    finish()

    assert endpoints["posted"] == []


def test_a_candidate_or_interview_gone_since_tells_nobody(endpoints, companies_api):
    endpoints["hook"]("https://a.example/x")
    companies_api["missing"] = True

    finish()

    assert endpoints["posted"] == []


def test_an_address_no_longer_public_or_an_unreadable_secret_is_skipped(endpoints, monkeypatch):
    endpoints["hook"]("https://a.example/x")
    endpoints["public"] = False

    finish()

    assert endpoints["posted"] == []

    monkeypatch.setattr(delivery.settings, "api_encryption_key", "")
    endpoints["public"] = True
    finish("e2")

    assert endpoints["posted"] == []


def test_an_address_that_doesnt_resolve_now_is_retried(endpoints):
    endpoints["hook"]("https://a.example/x")
    endpoints["hook"]("https://flaky.example/x")
    endpoints["unresolved"].add("https://flaky.example/x")

    with pytest.raises(delivery.DeliveryFailed):
        finish()

    endpoints["unresolved"].clear()
    finish()

    assert [item[0] for item in endpoints["posted"]] == [
        "https://a.example/x",
        "https://flaky.example/x",
    ]


def test_companies_busy_raises_so_the_event_comes_again(endpoints, monkeypatch):
    endpoints["hook"]("https://a.example/x")
    real = delivery.companies.interview

    async def busy(company_id, interview_id):
        raise HTTPException(503, "Unavailable")

    monkeypatch.setattr(delivery.companies, "interview", busy)

    with pytest.raises(HTTPException):
        finish()

    assert endpoints["posted"] == []

    monkeypatch.setattr(delivery.companies, "interview", real)
    finish()
    finish()

    assert [item[0] for item in endpoints["posted"]] == ["https://a.example/x"]


def test_a_deleted_company_loses_its_keys_and_web_hooks(monkeypatch):
    removed = []

    async def remove_keys(company_id):
        removed.append(("keys", company_id))

    async def remove_hooks(company_id):
        removed.append(("webhooks", company_id))

    monkeypatch.setattr(events.keys, "remove_company", remove_keys)
    monkeypatch.setattr(events.webhooks, "remove_company", remove_hooks)
    asyncio.run(events.handle("company.deleted", {"company_id": str(COMPANY)}, "e1"))
    asyncio.run(events.handle("interview.ready", {"interview_id": str(INTERVIEW)}, "e2"))

    assert removed == [("keys", COMPANY), ("webhooks", COMPANY)]
