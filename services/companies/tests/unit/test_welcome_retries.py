import asyncio
import uuid

import httpx
import pytest
from prepza_common import http

from app.constants.billing import WELCOME_ATTEMPTS

# The real call: conftest replaces billing.welcome_company for the other tests.
from app.integrations.billing import welcome_company


def answering(*codes):
    """A billing that answers each call with the next status code; returns the calls made."""
    calls = []

    def handler(request):
        calls.append(request.url.path)

        return httpx.Response(codes[len(calls) - 1])

    return httpx.AsyncClient(transport=httpx.MockTransport(handler)), calls


def test_a_welcome_whose_answer_was_lost_is_asked_again_for_the_same_company(monkeypatch):
    client, calls = answering(503, 204)
    monkeypatch.setattr(http, "get_client", lambda: client)
    company_id = uuid.uuid4()

    asyncio.run(welcome_company(company_id, "ann@example.com", None, []))

    assert calls == [f"/internal/companies/{company_id}/welcome"] * 2


def test_a_welcome_failing_every_time_fails_after_its_tries(monkeypatch):
    client, calls = answering(*[503] * WELCOME_ATTEMPTS)
    monkeypatch.setattr(http, "get_client", lambda: client)

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(welcome_company(uuid.uuid4(), "ann@example.com", None, []))

    assert len(calls) == WELCOME_ATTEMPTS
