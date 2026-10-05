from enum import StrEnum
from http import HTTPStatus

from prepza_common.constants import (  # noqa: F401 (re-exported)
    INTERVIEWS_PER_DAY,
    MAX_INTERVIEWS_WITHOUT_CANDIDATES,
    MAX_OWNED_COMPANIES,
)

# The longest search through candidates' emails (an email is at most 254 characters).
MAX_SEARCH_LENGTH = 254


# How an interview's candidates are listed: best grade first, or newest invite first.
class CandidateSort(StrEnum):
    GRADE = "grade"
    DATE = "date"


class InviteStatus(StrEnum):
    INVITED = "invited"
    # The invite email bounced or was marked as spam, before the candidate opened the invite.
    UNDELIVERED = "undelivered"
    IN_PROCESS = "in_process"
    FINISHED = "finished"
    # The candidate deleted their account: their email and results are gone.
    DELETED = "deleted"
    # Never started within INVITE_EXPIRY_DAYS of being sent; sending it again revives it.
    EXPIRED = "expired"


# Statuses of an invite the candidate hasn't started: its credits are set aside, not charged.
NOT_STARTED = (InviteStatus.INVITED, InviteStatus.UNDELIVERED, InviteStatus.EXPIRED)


# Candidate invites, with the candidate's results, are kept this long after they're sent.
CANDIDATE_RETENTION_DAYS = 365
# An invite never started this long after it was last sent expires, and its credits come back.
INVITE_EXPIRY_DAYS = 30
# Inviting many at once: the most emails one list may hold, and the longest text pasted or
# uploaded (a CSV export with other columns is fine; only its emails count).
MAX_BULK_INVITES = 100
TOO_MANY_EMAILS = "At most 100 emails at once."
NO_EMAILS = "No emails found."
MAX_BULK_TEXT_LENGTH = 50_000
# Anything in a list that looks like an email; each is checked properly after.
EMAIL_PATTERN = r"[^\s,;<>()\"']+@[^\s,;<>()\"']+"


# Why an email from a list wasn't invited.
class SkipReason(StrEnum):
    INVALID = "invalid"
    # Over the member's email limits for now.
    LIMIT = "limit"
    # The company ran out of credits; the rest of the list wasn't tried.
    NO_CREDITS = "no_credits"
    FAILED = "failed"


# What a refused invite's HTTP status means for the list; any other is FAILED.
SKIP_REASONS = {
    HTTPStatus.PAYMENT_REQUIRED: SkipReason.NO_CREDITS,
    HTTPStatus.TOO_MANY_REQUESTS: SkipReason.LIMIT,
}


# An invite not started this long after it was last sent gets one reminder email.
REMINDER_AFTER_DAYS = 3
# Reminders queued per daily run; the rest go the next day.
REMINDERS_PER_RUN = 500
TOO_MANY_COMPANIES = "You can own at most 3 companies."
# Company names are unique across prepza, ignoring case, and short enough for a heading.
MAX_COMPANY_NAME_LENGTH = 45
COMPANY_NAME_TAKEN = "A company with this name already exists."
TOO_MANY_INTERVIEWS = "Your company can generate up to 10 interviews a day. Try again tomorrow."
TOO_MANY_WITHOUT_CANDIDATES = (
    "Invite a candidate to one of your interviews before generating another: up to 3 interviews "
    "can wait without candidates."
)
# A shareable link whose company has no credits left for another candidate.
LINK_CLOSED = "This test isn't taking new candidates right now."
# Random bytes in a shareable link's code.
LINK_TOKEN_BYTES = 12


# What a company can narrow its candidates to: an invite status, or a result: reached the pass
# mark, or flagged by integrity signals. A deleted candidate's row has no email to show.
class CandidateFilter(StrEnum):
    INVITED = InviteStatus.INVITED
    IN_PROCESS = InviteStatus.IN_PROCESS
    FINISHED = InviteStatus.FINISHED
    PASSED = "passed"
    FLAGGED = "flagged"
    UNDELIVERED = InviteStatus.UNDELIVERED
    EXPIRED = InviteStatus.EXPIRED


# Filters that need every candidate's results from rounds, not just their invite.
RESULT_FILTERS = (CandidateFilter.PASSED, CandidateFilter.FLAGGED)
# The integrity signals rounds counts per candidate.
SIGNAL_KEYS = ("tab_leaves", "copies", "fast_answers")
