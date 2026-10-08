from pydantic import BaseModel

from app.constants.unsubscribe import UnsubscribeType


class UnsubscribeOut(BaseModel):
    """What a link stops, for the page to say before it's confirmed: the type, and for a
    candidate's link the company's name."""

    type: UnsubscribeType
    company: str | None = None
