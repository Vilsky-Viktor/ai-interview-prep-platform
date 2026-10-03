from enum import StrEnum

from prepza_common.constants import MAX_SHARES  # noqa: F401 (re-exported)


class SetKind(StrEnum):
    PREPARATION = "preparation"
    INTERVIEW = "interview"


class OwnerType(StrEnum):
    USER = "user"
    COMPANY = "company"


class Visibility(StrEnum):
    PRIVATE = "private"
    PUBLIC = "public"


class Access(StrEnum):
    """How the current user relates to a preparation."""

    OWNER = "owner"
    JOINED = "joined"
    PUBLIC = "public"


TOO_MANY_SHARES = "A kit can be shared with at most 30 people."
