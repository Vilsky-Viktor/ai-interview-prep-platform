from pydantic import BaseModel, Field


class TitleCheckIn(BaseModel):
    # Any stored title: ones from before the rename limit run up to 200 characters.
    title: str = Field(min_length=1, max_length=200)


class TitleCheckOut(BaseModel):
    has_company: bool = Field(
        description="True when the title names a company or organization, not just its products"
    )
