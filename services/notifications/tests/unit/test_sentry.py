from unittest import mock

import sentry_sdk

from app.integrations.sentry import init_sentry, scrub


def test_emails_are_scrubbed_from_events():
    assert scrub({"message": "Resend refused bob@example.com", "extra": [{"to": "a@b.io"}]}) == {
        "message": "Resend refused [email]",
        "extra": [{"to": "[email]"}],
    }


def test_nothing_is_sent_without_a_dsn(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)

    with mock.patch.object(sentry_sdk, "init") as init:
        init_sentry()

    init.assert_not_called()
