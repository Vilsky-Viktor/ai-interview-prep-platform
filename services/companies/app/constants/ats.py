from enum import StrEnum


class AtsProvider(StrEnum):
    """The applicant tracking systems a company can connect."""

    WORKABLE = "workable"


class ConnectionStatus(StrEnum):
    # Working; or its key stopped working (revoked or expired) and needs reconnecting.
    CONNECTED = "connected"
    BROKEN = "broken"


# Workable's API for one account, by its subdomain (acme for acme.workable.com).
WORKABLE_API = "https://{subdomain}.workable.com/spi/v3"
# A subdomain as Workable allows it.
WORKABLE_SUBDOMAIN = r"^[a-z0-9][a-z0-9-]{0,62}$"
# The most jobs one page of Workable's list returns, and how many pages are read at most.
WORKABLE_PAGE = 100
WORKABLE_MAX_PAGES = 10
# Seconds to wait for an ATS's answer.
ATS_TIMEOUT_SECONDS = 15


class CandidateStatus(StrEnum):
    """A candidate the ATS sent: waiting for the interview to be ready (or being invited right
    now), invited, or not invited for `reason`."""

    WAITING = "waiting"
    INVITING = "inviting"
    INVITED = "invited"
    FAILED = "failed"


# An invite claimed this long ago and still not settled was cut off (the server stopped
# mid-invite): it can be claimed again.
STALE_CLAIM_MINUTES = 10


class FailReason(StrEnum):
    CREDITS = "credits"
    LIMIT = "limit"
    PAUSED = "paused"
    OTHER = "other"


# The Workable event that sends a candidate: moved into a linked job's stage.
WORKABLE_MOVED = "candidate_moved"
# Where Workable sends it, one address per linked job (Workable wants each target unique).
WORKABLE_WEBHOOK = "{site}/api/companies/webhooks/ats/workable/{link_id}"
