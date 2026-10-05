from pydantic import BaseModel, Field

from app.constants.verification import MAX_WEBSITE_LENGTH


class WebsiteIn(BaseModel):
    """The company's website as typed; empty removes it, and the verification with it."""

    website: str = Field(default="", max_length=MAX_WEBSITE_LENGTH)


class VerificationOut(BaseModel):
    website_domain: str | None
    # Set once an owner or admin with a verified email on the domain confirms it.
    verified_domain: str | None
