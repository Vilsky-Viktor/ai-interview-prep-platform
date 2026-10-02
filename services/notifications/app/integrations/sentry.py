import os
import re

import sentry_sdk

from app.constants.sentry import DEFAULT_TRACES_SAMPLE_RATE, EMAIL_PATTERN, REDACTED_EMAIL


def scrub(value):
    """Replaces every email address in an event, however deep it sits; every event here is
    about an email to someone."""
    if isinstance(value, str):
        return re.sub(EMAIL_PATTERN, REDACTED_EMAIL, value)

    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items()}

    if isinstance(value, list):
        return [scrub(item) for item in value]

    return value


def init_sentry() -> None:
    """Reports failed emails and crashes to Sentry when SENTRY_DSN is set."""
    dsn = os.getenv("SENTRY_DSN")

    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
        release=os.getenv("SENTRY_RELEASE") or None,
        server_name="notifications",
        traces_sample_rate=float(
            os.getenv("SENTRY_TRACES_SAMPLE_RATE", DEFAULT_TRACES_SAMPLE_RATE)
        ),
        send_default_pii=False,
        before_send=lambda event, hint: scrub(event),
    )
    sentry_sdk.set_tag("service", "notifications")
