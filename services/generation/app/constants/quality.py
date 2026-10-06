from enum import StrEnum


class QualityFlag(StrEnum):
    """Why the library sent a question to the verifier; mirrors the library's flags."""

    WRONG_KEY = "wrong_key"
    REWRITE = "rewrite"
    WEAK_OPTIONS = "weak_options"


# A batch that ended this way is sent again.
BATCH_RETRY_STATUSES = ("failed", "expired", "cancelled")
# Key checks sent in one batch (each is looked up in the library first).
MAX_BATCH_KEY_CHECKS = 500
# One key-check run at a time: a slow run isn't joined by the next scheduled one. The lock
# outlasts a run's longest time (the scheduler's 10-minute deadline).
KEY_CHECK_LOCK_KEY = "lock:key-check-batches"
KEY_CHECK_LOCK_SECONDS = 10 * 60
# A new test's or template's answer keys checked by the verifier before it's ready: this many
# random questions a topic (about $0.001 each).
KEY_CHECKS_PER_TOPIC = 1
# Verifier jobs a day, for everyone together: a ceiling on what flags can spend on rewrites
# (a few cents each). A superadmin's "Fix now" isn't counted.
DAILY_VERIFY_LIMIT = 300
VERIFY_BUDGET_KEY = "budget:verify"
VERIFY_PAUSED = "Today's limit for question checks is reached; the question is checked later."
