from enum import StrEnum


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
# Companies one person may own; the welcome credits come with the first one only.
MAX_OWNED_COMPANIES = 3
TOO_MANY_COMPANIES = "You can own at most 3 companies."
# Interviews are free to generate, so each company may start this many a day.
INTERVIEWS_PER_DAY = 10
TOO_MANY_INTERVIEWS = "Your company can generate up to 10 interviews a day. Try again tomorrow."
