from enum import StrEnum


class SetKind(StrEnum):
    INTERVIEW = "interview"
    # Made by a superadmin (Phase 2 of docs/company-plan.md); the question bank reuses theirs.
    TEMPLATE = "template"


class OwnerType(StrEnum):
    COMPANY = "company"
    # A template belongs to prepza itself.
    PLATFORM = "platform"


PLATFORM_OWNER = "prepza"


class Stage(StrEnum):
    """A template question's place in the bank; it only ever moves forward."""

    # Used in company tests only; its answer is never shown.
    PRIVATE = "private"
    # Served enough candidates: new tests stop taking it, tests that have it keep it.
    RETIRING = "retiring"
    # No active test has it any more: free practice for talents, shown with its answer.
    REVEALED = "revealed"


# A new template reveals every REVEALED_EVERY-th question of each topic at once, so practice has
# questions from the start (about a third); the rest start private.
REVEALED_EVERY = 3
