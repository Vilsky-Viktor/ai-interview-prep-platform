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
