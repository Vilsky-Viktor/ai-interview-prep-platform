from pydantic import BaseModel, Field

from app.constants.quality import QualityFlag
from app.schemas.regenerate import RegeneratedOption


class VerifyIn(BaseModel):
    flag: QualityFlag


class ReportNote(BaseModel):
    reason: str
    comment: str


class QuestionQuality(BaseModel):
    text: str
    options: list[RegeneratedOption]
    answers: int
    option_picks: dict[str, int]
    reports: list[ReportNote]


class KeyCheck(BaseModel):
    correct_index: int | None = Field(
        description="The number of the one option that is correct, or null when none of them "
        "is correct or more than one could be defended as correct."
    )
