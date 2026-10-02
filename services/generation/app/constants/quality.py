from enum import StrEnum


class QualityFlag(StrEnum):
    """Why the library sent a question to the verifier; mirrors the library's flags."""

    WRONG_KEY = "wrong_key"
    REWRITE = "rewrite"
    WEAK_OPTIONS = "weak_options"


# The key check is rare and must be right, so it thinks harder than generation does.
VERIFY_REASONING_EFFORT = "medium"
# Key checks go to OpenAI in one batch every this many minutes; results come back within 24 hours.
KEY_CHECK_MINUTES = set(range(0, 60, 10))
# A batch that ended this way is sent again.
BATCH_RETRY_STATUSES = ("failed", "expired", "cancelled")
