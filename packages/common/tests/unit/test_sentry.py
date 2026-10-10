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


def test_urls_keep_only_their_scheme_and_host_and_queries_are_dropped():
    hook = "https://hooks.slack.com/services/T0/B0/secret"
    event = {
        "request": {"url": "https://api.prepza.com/invites/token123", "query_string": "t=1"},
        "breadcrumbs": [
            {"category": "httplib", "data": {"url": hook, "http.query": "key=1"}},
        ],
        "spans": [{"description": f"POST {hook}", "data": {"url": "http://a:b@x.io:8080/p?q"}}],
        "exception": {"values": [{"value": f"Client error '404 Not Found' for url '{hook}'"}]},
    }

    assert scrub(event) == {
        "request": {"url": "https://api.prepza.com"},
        "breadcrumbs": [{"category": "httplib", "data": {"url": "https://hooks.slack.com"}}],
        "spans": [
            {"description": "POST https://hooks.slack.com", "data": {"url": "http://x.io:8080"}}
        ],
        "exception": {
            "values": [{"value": "Client error '404 Not Found' for url 'https://hooks.slack.com'"}]
        },
    }


def test_nothing_is_sent_without_a_dsn(monkeypatch):
    monkeypatch.delenv("BACKEND_SENTRY_DSN", raising=False)

    with mock.patch.object(sentry_sdk, "init") as init:
        init_sentry("rounds")

    init.assert_not_called()


def test_with_a_dsn_no_personal_data_is_sent(monkeypatch):
    monkeypatch.setenv("BACKEND_SENTRY_DSN", "https://key@example.ingest.sentry.io/1")

    with mock.patch.object(sentry_sdk, "init") as init:
        init_sentry("rounds")

    options = init.call_args.kwargs
    assert options["send_default_pii"] is False
    assert options["max_request_body_size"] == "never"
    assert options["server_name"] == "rounds"
    assert options["before_send"] is sentry.before_send
    assert options["before_send_transaction"] is sentry.before_send


def test_a_service_can_keep_variables_values_out_of_stack_traces(monkeypatch):
    monkeypatch.setenv("BACKEND_SENTRY_DSN", "https://key@example.ingest.sentry.io/1")

    with mock.patch.object(sentry_sdk, "init") as init:
        init_sentry("assistant", local_variables=False)

    assert init.call_args.kwargs["include_local_variables"] is False
