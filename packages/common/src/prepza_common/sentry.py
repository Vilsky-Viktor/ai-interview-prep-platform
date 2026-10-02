import os
import re

import sentry_sdk
from prepza_common.constants import (
    DEFAULT_TRACES_SAMPLE_RATE,
    EMAIL_PATTERN,
    REDACTED_EMAIL,
)


def scrub(value):
    """Replaces every email address in an event, however deep it sits, before it leaves us."""
    if isinstance(value, str):
        return re.sub(EMAIL_PATTERN, REDACTED_EMAIL, value)

    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items()}

    if isinstance(value, list):
        return [scrub(item) for item in value]

    return value


def before_send(event, hint):
    return scrub(event)


def init_sentry(service: str, integrations: list | None = None) -> None:
    """Reports errors to Sentry when SENTRY_DSN is set; local development and tests send nothing.

    No personal data: no IPs, cookies, headers or request bodies, and emails are scrubbed. A
    signed-in user is known only by their id (see auth.current_user).
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
        integrations=integrations or [],
        before_send=before_send,
        before_send_transaction=before_send,
    )
    sentry_sdk.set_tag("service", service)
