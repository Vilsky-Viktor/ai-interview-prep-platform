from enum import StrEnum


class QualityFlag(StrEnum):
    """Why the library sent a question to the verifier; mirrors the library's flags."""

    WRONG_KEY = "wrong_key"
    REWRITE = "rewrite"
    WEAK_OPTIONS = "weak_options"


# A batch that ended this way is sent again.
BATCH_RETRY_STATUSES = ("failed", "expired", "cancelled")
# A new test's or template's answer keys checked by the verifier before it's ready: this many
# random questions a topic (about $0.001 each).
KEY_CHECKS_PER_TOPIC = 1
