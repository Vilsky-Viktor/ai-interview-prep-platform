from typing import Annotated

from prepza_common.constants import MAX_TITLE_LENGTH, MIN_TITLE_LENGTH, TITLE_TOO_SHORT
from pydantic import AfterValidator, Field


def titled(value: str) -> str:
    """An edited title without spaces at either end, refused (422, TITLE_TOO_SHORT, translated)
    under MIN_TITLE_LENGTH characters."""
    value = value.strip()

    if len(value) < MIN_TITLE_LENGTH:
        raise ValueError(TITLE_TOO_SHORT)

    return value


# A test's or a template's title as a member or superadmin edits it.
Title = Annotated[str, Field(max_length=MAX_TITLE_LENGTH), AfterValidator(titled)]
