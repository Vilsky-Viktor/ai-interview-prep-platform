from enum import StrEnum


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


# People a private kit can be shared with, counting accepted and pending invites.
MAX_SHARES = 30
TOO_MANY_SHARES = "A kit can be shared with at most 30 people."
