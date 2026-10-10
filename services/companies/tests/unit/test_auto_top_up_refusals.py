import asyncio
import uuid

import httpx
import pytest
from fastapi import HTTPException
from prepza_common import http

from app.integrations import billing


@pytest.mark.parametrize("code", [403, 422])
def test_billings_refusal_reaches_the_user_unchanged(monkeypatch, code):
    """A choice it doesn't offer, or a running top-up paid by someone else's card."""
    detail = "Only the person whose card pays for it can change it."
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(code, json={"detail": detail}))
    )
    monkeypatch.setattr(http, "get_client", lambda: client)

    with pytest.raises(HTTPException) as refused:
        asyncio.run(billing.turn_on_auto_top_up(uuid.uuid4(), {}, "bob"))

    assert (refused.value.status_code, refused.value.detail) == (code, detail)
