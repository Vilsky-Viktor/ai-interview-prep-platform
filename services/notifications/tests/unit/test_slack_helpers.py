import asyncio
import base64

import httpx
import pytest
from prepza_common.notifications import NotificationKind, Recipient, notification

from app.helpers.slack import message, read_state, signed_state
from app.integrations import slack

SECRET = "test-secret-that-is-at-least-32-bytes"


def test_a_state_names_its_company_user_and_nonce_until_it_expires():
    state = signed_state(SECRET, "c1", "u1", expires=1_000, nonce="n1")

    assert read_state(SECRET, state, now=999) == ("c1", "u1", "n1")
    assert read_state(SECRET, state, now=1_001) is None


def test_a_state_signed_with_another_secret_or_changed_is_refused():
    state = signed_state(SECRET, "c1", "u1", expires=1_000, nonce="n1")
    forged = base64.urlsafe_b64encode(
        base64.urlsafe_b64decode(state).replace(b"c1|", b"c2|")
    ).decode()

    assert read_state("another-secret-that-is-32-bytes-long", state, now=0) is None
    assert read_state(SECRET, forged, now=0) is None
    assert read_state(SECRET, "not-a-state", now=0) is None


def event(kind, **data):
    return notification(Recipient.COMPANY, "c1", kind, "/companies/c1/x", **data)


def test_a_finished_candidate_reads_with_the_grade_and_links_to_prepza():
    text = message(
        event(NotificationKind.CANDIDATE_FINISHED, email="a@b.c", title="Backend", grade=82),
        "https://prepza.ai",
    )

    assert (
        text == "a@b.c finished “Backend”: 82%. <https://prepza.ai/companies/c1/x|Open in prepza>"
    )


def test_a_not_invited_candidate_names_the_ats_and_why():
    text = message(
        event(
            NotificationKind.ATS_NOT_INVITED,
            email="a@b.c",
            title="Backend",
            ats="Greenhouse",
            reason="credits",
        ),
        "https://prepza.ai",
    )

    assert text.startswith("a@b.c from Greenhouse wasn't invited to “Backend”: out of credits.")


def test_what_people_wrote_is_shown_not_read_as_slack_markup():
    text = message(
        event(NotificationKind.INTERVIEW_READY, title="<!channel> R&D <https://x|y>"),
        "https://prepza.ai",
    )

    assert text == (
        "The interview “&lt;!channel&gt; R&amp;D &lt;https://x|y&gt;” is ready."
        " <https://prepza.ai/companies/c1/x|Open in prepza>"
    )


def test_a_kind_slack_doesnt_get_has_no_message():
    assert message(event(NotificationKind.QUESTION_FLAGGED, title="Acme"), "https://x") is None


@pytest.mark.parametrize("answer", [httpx.Response(404), httpx.Response(400, text="no_service")])
def test_a_web_hook_slack_says_is_gone(monkeypatch, answer):
    monkeypatch.setattr(slack.http, "get_client", lambda: client(answer))

    with pytest.raises(slack.WebhookGone):
        asyncio.run(slack.post("https://hooks.slack.com/x", "hi"))


@pytest.mark.parametrize("status", [429, 500, 503])
def test_slack_busy_or_down_is_an_http_error_not_a_gone_web_hook(monkeypatch, status):
    monkeypatch.setattr(slack.http, "get_client", lambda: client(httpx.Response(status)))

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(slack.post("https://hooks.slack.com/x", "hi"))


def test_a_message_slack_turns_down_says_why(monkeypatch):
    answer = httpx.Response(400, text="invalid_payload")
    monkeypatch.setattr(slack.http, "get_client", lambda: client(answer))

    with pytest.raises(slack.SlackRefused, match="invalid_payload"):
        asyncio.run(slack.post("https://hooks.slack.com/x", "hi"))


def test_an_approved_code_becomes_the_channels_web_hook(monkeypatch):
    body = {
        "ok": True,
        "access_token": "xoxb-1",
        "team": {"name": "Acme"},
        "incoming_webhook": {"channel": "#hiring", "url": "https://hooks.slack.com/x"},
    }
    monkeypatch.setattr(slack.http, "get_client", lambda: client(httpx.Response(200, json=body)))

    assert asyncio.run(slack.exchange("code")) == {
        "team": "Acme",
        "channel": "#hiring",
        "url": "https://hooks.slack.com/x",
        "token": "xoxb-1",
    }


def test_a_refused_code_says_why(monkeypatch):
    answer = httpx.Response(200, json={"ok": False, "error": "invalid_code"})
    monkeypatch.setattr(slack.http, "get_client", lambda: client(answer))

    with pytest.raises(slack.SlackRefused, match="invalid_code"):
        asyncio.run(slack.exchange("code"))


def client(answer: httpx.Response) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(lambda request: answer))
