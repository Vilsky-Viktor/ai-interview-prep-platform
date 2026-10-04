from enum import StrEnum


class QualityFlag(StrEnum):
    """Why the library sent a question to the verifier; mirrors the library's flags."""

    WRONG_KEY = "wrong_key"
    REWRITE = "rewrite"
    WEAK_OPTIONS = "weak_options"


# A batch that ended this way is sent again.
BATCH_RETRY_STATUSES = ("failed", "expired", "cancelled")
