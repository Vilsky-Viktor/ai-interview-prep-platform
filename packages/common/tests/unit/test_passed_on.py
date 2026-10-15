import asyncio
import uuid

import httpx
import pytest
from fastapi import HTTPException
from prepza_common import company_invites, http
from prepza_common.http import passed_on


def answer(code: int, body=None) -> httpx.Response:
    return httpx.Response(code, json=body, request=httpx.Request("GET", "http://x"))


def test_a_refusal_asked_for_reaches_the_client_with_its_reason():
    with pytest.raises(HTTPException) as refused:
        passed_on(answer(402, {"detail": "Not enough credits."}), {402, 409})

    assert (refused.value.status_code, refused.value.detail) == (402, "Not enough credits.")


def test_any_refusal_passes_without_codes_and_others_raise_with_them():
    with pytest.raises(HTTPException):
        passed_on(answer(422, {"detail": "Invalid"}))

    with pytest.raises(httpx.HTTPStatusError):
        passed_on(answer(500), {402})

    assert passed_on(answer(200, {"ok": True})).json() == {"ok": True}


def test_an_invite_through_companies_returns_its_id_or_its_refusal(monkeypatch):
    made = uuid.uuid4()
    answers = iter(
        [
            httpx.Response(201, json={"invite_id": str(made)}),
            httpx.Response(409, json={"detail": "Interview is still being generated"}),
        ]
    )
    client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: next(answers)))
    monkeypatch.setattr(http, "get_client", lambda: client)
    body = {"email": "ann@example.com", "sender_id": "u1"}

    found = asyncio.run(company_invites.invite("http://companies", "t", made, body, {409}))

    assert found == made
    with pytest.raises(HTTPException) as refused:
        asyncio.run(company_invites.invite("http://companies", "t", made, body, {409}))
    assert refused.value.detail == "Interview is still being generated"
