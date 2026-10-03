from typing import Literal

from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES
from pydantic import BaseModel

# A supported language's code (LANGUAGES).
Language = Literal[tuple(LANGUAGES)]


class User(BaseModel):
    uid: str
    email: str
    email_verified: bool
    name: str | None = None
    language: Language = DEFAULT_LANGUAGE
