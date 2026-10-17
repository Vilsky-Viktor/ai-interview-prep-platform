import asyncio

import httpx
import pytest
from prepza_common.ai_constants import LIMIT_HIT

from app.config.settings import settings
from app.integrations import resend
from app.integrations.resend import EmailRefused, ResendBusy
from app.models.email import Email

EMAIL = Email(to="ann@example.com", subject="Hi", html="<p>Hi</p>", text="Hi")


def send(monkeypatch, response: httpx.Response) -> None:
    """Sends EMAIL to a Resend that answers `response`."""

    def answer(request):
        return response

    client = httpx.AsyncClient(transport=httpx.MockTransport(answer))
    monkeypatch.setattr(resend.http, "get_client", lambda: client)
    monkeypatch.setattr(settings, "resend_api_key", "re_test")
    asyncio.run(resend.send(EMAIL, "k"))


def hits(published) -> list[tuple]:
    return [
        (data["limit"], data["kind"], data["scope"])
        for kind, data in published
        if kind == LIMIT_HIT
    ]


@pytest.mark.parametrize(
    ("body", "limit"),
    [
        ({"name": "rate_limit_exceeded"}, "RESEND_RATE_LIMIT"),
        ({"name": "daily_quota_exceeded"}, "RESEND_DAILY_QUOTA"),
    ],
)
def test_resends_limits_are_recorded_as_its_own_and_retried(monkeypatch, published, body, limit):
    with pytest.raises(ResendBusy):
        send(monkeypatch, httpx.Response(429, json=body))

    assert hits(published) == [(limit, "provider:resend", "everyone")]


def test_a_429_without_a_body_is_resends_rate_limit(monkeypatch, published):
    with pytest.raises(ResendBusy):
        send(monkeypatch, httpx.Response(429, text="Too many requests"))

    assert hits(published) == [("RESEND_RATE_LIMIT", "provider:resend", "everyone")]


def test_a_sent_or_refused_email_is_no_limit_hit(monkeypatch, published):
    send(monkeypatch, httpx.Response(200, json={"id": "e-1"}))

    with pytest.raises(EmailRefused):
        send(monkeypatch, httpx.Response(422, json={"name": "validation_error"}))

    assert published == []
