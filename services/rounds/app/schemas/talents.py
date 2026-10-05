from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.constants.talents import LINKEDIN_HOST, MAX_TALENT_URL_LENGTH, NOT_LINKEDIN


class TalentLinkIn(BaseModel):
    """A LinkedIn link is the talent's consent to be suggested; none declines (or withdraws)."""

    url: HttpUrl | None = Field(default=None, max_length=MAX_TALENT_URL_LENGTH)

    @field_validator("url")
    @classmethod
    def linkedin_only(cls, value: HttpUrl | None) -> HttpUrl | None:
        host = (value.host or "").lower() if value else ""

        if value and not (host == LINKEDIN_HOST or host.endswith(f".{LINKEDIN_HOST}")):
            raise ValueError(NOT_LINKEDIN)

        return value


class TalentLinkOut(BaseModel):
    """Whether the talent has answered yet, and their link while they agree to be suggested."""

    decided: bool
    url: str | None


class SuggestionsIn(BaseModel):
    """The templates for roles like a company's test."""

    template_ids: list[UUID]


class SuggestedTalent(BaseModel):
    """What a company sees of a talent: name, LinkedIn, and their first-round grade on the
    closest template they practised."""

    name: str
    url: str
    grade: int
    template_id: UUID
