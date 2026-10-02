from unittest import mock

import sentry_sdk
from prepza_common import sentry
from prepza_common.sentry import init_sentry, scrub


def test_emails_are_scrubbed_everywhere_in_an_event():
    event = {
        "message": "Invite to bob@example.com failed",
        "exception": {"values": [{"value": "No inbox for Ann.Lee+jobs@mail.co.uk"}]},
        "breadcrumbs": [{"data": {"email": "carol@example.org", "count": 3}}],
    }

    assert scrub(event) == {
        "message": "Invite to [email] failed",
        "exception": {"values": [{"value": "No inbox for [email]"}]},
        "breadcrumbs": [{"data": {"email": "[email]", "count": 3}}],
    }


def test_nothing_is_sent_without_a_dsn(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)

    with mock.patch.object(sentry_sdk, "init") as init:
        init_sentry("rounds")

    init.assert_not_called()


def test_with_a_dsn_no_personal_data_is_sent(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "https://key@example.ingest.sentry.io/1")

    with mock.patch.object(sentry_sdk, "init") as init:
        init_sentry("rounds")

    options = init.call_args.kwargs
    assert options["send_default_pii"] is False
    assert options["max_request_body_size"] == "never"
    assert options["server_name"] == "rounds"
    assert options["before_send"] is sentry.before_send
