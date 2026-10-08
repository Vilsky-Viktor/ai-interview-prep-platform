from typing import Literal

from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES, LEVELS
from pydantic import BaseModel

# A supported language's code (LANGUAGES).
Language = Literal[tuple(LANGUAGES)]
# A test's level (LEVELS).
Level = Literal[LEVELS]


class User(BaseModel):
    uid: str
    email: str
    email_verified: bool
    name: str | None = None
    language: Language = DEFAULT_LANGUAGE


class UserEmailIn(BaseModel):
    """The account's email, sent in the body of library's calls to delete or export a user's
    data, so request logs don't record it."""

    email: str
