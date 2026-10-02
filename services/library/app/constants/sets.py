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


