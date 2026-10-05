from pydantic import BaseModel, Field


class SuggestedTalentOut(BaseModel):
    """What a company sees of a suggested talent: their name, LinkedIn and first-round grade on
    a practice test for a similar role. Nothing else."""

    name: str
    url: str
    grade: int


class HideTalentIn(BaseModel):
    url: str = Field(max_length=300)
