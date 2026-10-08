import os
import re

import sentry_sdk
from prepza_common.constants import (
    DEFAULT_TRACES_SAMPLE_RATE,
    EMAIL_PATTERN,
    QUERY_FIELDS,
    REDACTED_EMAIL,
    URL_PATTERN,
    URL_SCRUBBED,
)


def scrub(value):
    """Replaces every email address in an event, however deep it sits, and cuts every URL to its
    scheme and host, before it leaves us: outgoing calls' URLs (web hooks, Slack) are secrets."""
    if isinstance(value, str):
        return re.sub(EMAIL_PATTERN, REDACTED_EMAIL, re.sub(URL_PATTERN, URL_SCRUBBED, value))

    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items() if key not in QUERY_FIELDS}

    if isinstance(value, list):
        return [scrub(item) for item in value]

    return value


def before_send(event, hint):
    return scrub(event)


def init_sentry(
    service: str, integrations: list | None = None, local_variables: bool = True
) -> None:
    """Reports errors to Sentry when SENTRY_DSN is set; local development and tests send nothing.

    No personal data or secrets: no IPs, cookies, headers or request bodies; emails are scrubbed
    and URLs cut to their host everywhere in an error or a trace, its breadcrumbs and spans
    included. A signed-in user is known only by their id (see auth.current_user). Without
    `local_variables`, a stack trace carries no variables' values (the assistant's hold
    conversations).
    """
    dsn = os.getenv("SENTRY_DSN")

    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
        release=os.getenv("SENTRY_RELEASE") or None,
        server_name=service,
        traces_sample_rate=float(
            os.getenv("SENTRY_TRACES_SAMPLE_RATE", DEFAULT_TRACES_SAMPLE_RATE)
        ),
        send_default_pii=False,
        max_request_body_size="never",
        include_local_variables=local_variables,
        integrations=integrations or [],
        before_send=before_send,
        before_send_transaction=before_send,
    )
    sentry_sdk.set_tag("service", service)
