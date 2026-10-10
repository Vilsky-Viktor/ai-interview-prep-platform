from enum import StrEnum
from http import HTTPStatus

from prepza_common.constants import (  # noqa: F401 (re-exported)
    INTERVIEWS_PER_DAY,
    MAX_CANDIDATE_NAME_LENGTH,
    MAX_INTERVIEWS_WITHOUT_CANDIDATES,
    MAX_OWNED_COMPANIES,
)

# The longest search through candidates' emails and names (an email is at most 254 characters).
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
STARTED = (InviteStatus.IN_PROCESS, InviteStatus.FINISHED)
# Statuses of an invite still open: its link works and its credits are set aside (an expired
# one gave them back).
OPEN = (InviteStatus.INVITED, InviteStatus.UNDELIVERED, InviteStatus.IN_PROCESS)


# Candidate invites, with the candidate's results, are kept this long after they're sent.
CANDIDATE_RETENTION_DAYS = 365
# Invites deleted per batch of the daily retention run.
RETENTION_BATCH = 200
# An invite never started this long after it was last sent expires, and its credits come back.
INVITE_EXPIRY_DAYS = 30
# Inviting many at once: the most emails one list may hold, and the longest text pasted or
# uploaded (a CSV export with other columns is fine; only its emails count).
MAX_BULK_INVITES = 100
TOO_MANY_EMAILS = "At most 100 emails at once."
NO_EMAILS = "No emails found."
NAME_NEEDS_ONE_EMAIL = "A name goes with one email. In a list, write each as Name <email>."
# The longest list: characters pasted, or bytes of an uploaded file (the frontend checks a file's
# size against it before reading it). The messages name the same limits.
MAX_BULK_TEXT_LENGTH = 50_000
FILE_TOO_LARGE = "The file is too large (max 50 KB)."
LIST_TOO_LONG = "The list is too long (max 50,000 characters)."
# An uploaded list is a CSV or TXT file, by its name, and text: no NUL bytes, and few characters
# that couldn't be read (a renamed spreadsheet is mostly those).
LIST_FILE_TYPES = (".csv", ".txt")
NOT_A_LIST_FILE = "Only CSV or TXT files."
MAX_UNREADABLE_SHARE = 0.05
# Anything in a list that looks like an email; each is checked properly after.
EMAIL_PATTERN = r"[^\s,;<>()\"']+@[^\s,;<>()\"']+"


# Why a line of a list can't be used (one reason a line): it has no email, an email that isn't
# valid, or a name that isn't written as "Name <email>" or "email, Name".
class LineProblem(StrEnum):
    NO_EMAIL = "no_email"
    INVALID_EMAIL = "invalid_email"
    UNCLEAR_NAME = "unclear_name"


# Why an email from a list wasn't invited.
class SkipReason(StrEnum):
    INVALID = "invalid"
    # Over the member's email limits for now.
    LIMIT = "limit"
    # The company ran out of credits; the rest of the list wasn't tried.
    NO_CREDITS = "no_credits"
    # The candidate already started or finished: a list doesn't email them again.
    STARTED = "started"
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
# Invites expired per batch of the daily expiry run.
EXPIRIES_PER_BATCH = 200
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
LINK_CLOSED = "This interview isn't taking new candidates right now."
# Random bytes in a shareable link's code.
LINK_TOKEN_BYTES = 12
# New candidates a job-ad link takes in an hour, and one address starts across all links: a
# script with many accounts can't hold (or, picking an answer, spend) a company's credits faster.
LINK_STARTS_PER_HOUR = 30
LINK_STARTS_PER_IP_HOUR = 10


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

# Extra time a company can give a candidate who needs it, in percent of each question's time.
EXTRA_TIME_OPTIONS = (0, 25, 50, 100)
# Extra time is set before the candidate starts: their questions' time is fixed then.
EXTRA_TIME_STARTED = "Extra time can only be changed before the candidate starts."
