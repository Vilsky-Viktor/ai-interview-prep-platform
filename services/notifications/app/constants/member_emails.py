# The emails to prepza's users (company members) that a schedule sends: the activity digest and
# reminders. Each is sent once (storage/sent_emails.py); a run sends for at most RUN_SECONDS, and
# the next run, minutes later, goes on where it stopped.
from enum import StrEnum


class MemberEmail(StrEnum):
    """What a sent email was, in the sent log: the daily digest, or one kind of reminder."""

    DIGEST = "digest"
    LOW_CREDITS = "low_credits"
    NO_CANDIDATES = "no_candidates"
    REVIEW_WAITING = "review_waiting"


# Other services take at most this many ids in one call.
MAX_IDS_PER_CALL = 1000

# A run stops sending after this long, well within the scheduler's 60 seconds, and waits this
# long between two emails, so it stays under Resend's per-second limit with room for invites.
RUN_SECONDS = 40
SEND_INTERVAL_SECONDS = 0.6

# The digest covers the 24 hours before the start of the hour its runs are in, the same window
# for every run of a day.
DIGEST_HOURS = 24

# A reminder of each kind reaches a user at most once in REMINDER_DAYS.
REMINDER_DAYS = 7
# An interview nobody was invited to NO_CANDIDATES_DAYS after it was ready; one ready more than
# NO_CANDIDATES_WINDOW_DAYS ago (before reminders existed, or missed) isn't reminded about.
NO_CANDIDATES_DAYS = 3
NO_CANDIDATES_WINDOW_DAYS = 10
# Topics waiting for their review for REVIEW_WAITING_DAYS. Generation cancels a review left open
# for 14 days (its REVIEW_EXPIRY_DAYS), so interviews started more than REVIEW_STARTED_DAYS ago
# aren't looked at.
REVIEW_WAITING_DAYS = 1
REVIEW_STARTED_DAYS = 15
# Generation's status of a generation waiting for its topics' review.
AWAITING_REVIEW = "awaiting_review"

# The sent log keeps rows long enough to outlast every window above.
SENT_KEEP_DAYS = 30

# The pages emails link to.
COMPANIES_LINK = "/companies"
INTERVIEWS_LINK = "/companies/{company_id}/interviews"
INTERVIEW_LINK = "/companies/{company_id}/interviews/{interview_id}"
TOP_UP_LINK = "/top-up"
