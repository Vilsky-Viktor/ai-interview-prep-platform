from enum import StrEnum

from prepza_common.constants import (  # noqa: F401 (re-exported)
    INTERVIEWS_PER_DAY,
    MAX_OWNED_COMPANIES,
)


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
TOO_MANY_COMPANIES = "You can own at most 3 companies."
# Company names are unique across prepza, ignoring case.
COMPANY_NAME_TAKEN = "A company with this name already exists."
TOO_MANY_INTERVIEWS = "Your company can generate up to 10 interviews a day. Try again tomorrow."
