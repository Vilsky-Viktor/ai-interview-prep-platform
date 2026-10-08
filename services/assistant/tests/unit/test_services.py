import asyncio

import httpx
from prepza_common import http
from prepza_common.service_auth import token_caller

from app.constants.tool_calls import TOOL_TIMEOUT_SECONDS
from app.integrations import services


class FakeClient:
    def __init__(self):
        self.calls = []

    async def get(self, url, params, headers, timeout):
        self.calls.append((url, params, headers, timeout))

        return httpx.Response(200, json={})


def test_calls_go_as_the_user_and_companies_learns_its_the_assistant(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(http, "get_client", lambda: client)

    asyncio.run(services.get("companies", "/pause", {}, "user-token", "de"))
    asyncio.run(services.get("billing", "/catalog", {"a": 1}, "user-token", "en"))

    (url, _, headers, timeout), (other_url, params, other_headers, _) = client.calls
    assert (url, other_url, params) == (
        "http://companies/pause",
        "http://billing/catalog",
        {"a": 1},
    )
    assert headers["Authorization"] == "Bearer user-token"
    assert headers["Accept-Language"] == "de"
    assert timeout == TOOL_TIMEOUT_SECONDS
    # Signed for companies, by the assistant: companies audits the read as the assistant's.
    secret = "test-secret-that-is-at-least-32-bytes"
    assert token_caller(headers["X-Assistant"], secret, "companies") == "assistant"
    assert "X-Assistant" not in other_headers
