from pydantic import BaseModel, Field

from app.constants.logos import MAX_LOGO_BYTES


class LogoIn(BaseModel):
    """The logo image, base64-encoded."""

    image: str = Field(min_length=1, max_length=MAX_LOGO_BYTES * 4 // 3 + 4)


class LogoOut(BaseModel):
    logo_url: str | None


class BrandOut(BaseModel):
    """Who a candidate's interview is for, shown while they take it."""

    company: str
    logo_url: str | None
    # For the candidate invited through the API with a return_url: where "Continue" takes them
    # once they've finished, with their invite's id.
    return_url: str | None = None
