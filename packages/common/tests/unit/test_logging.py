import logging

from prepza_common.logging import configure_logging


def test_outgoing_request_addresses_are_not_logged(caplog):
    """A Slack web hook's address lets anyone post to the channel: the HTTP client's request
    lines, which hold it, stay out of the logs."""
    configure_logging()

    with caplog.at_level(logging.INFO):
        logging.getLogger("httpx").info("HTTP Request: POST https://hooks.slack.com/services/T/B/x")

    assert "hooks.slack.com" not in caplog.text
    assert logging.getLogger("httpx").getEffectiveLevel() == logging.WARNING
