from typing import Literal

from prepza_common.constants import DEFAULT_LANGUAGE
from pydantic import BaseModel

Language = Literal["en", "ru"]


class User(BaseModel):
    uid: str
    email: str
    email_verified: bool
    name: str | None = None
    language: Language = DEFAULT_LANGUAGE
