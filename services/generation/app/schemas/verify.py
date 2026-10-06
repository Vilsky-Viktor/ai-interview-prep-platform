from pydantic import BaseModel, Field

from app.constants.quality import QualityFlag
from app.schemas.regenerate import RegeneratedOption


class VerifyIn(BaseModel):
    flag: QualityFlag
    # A superadmin's "Fix now": a wrong key is checked at once, not in the next batch.
    now: bool = False


class ReportNote(BaseModel):
    reason: str
    comment: str


class QuestionQuality(BaseModel):
    text: str
    options: list[RegeneratedOption]
    answers: int
    option_picks: dict[str, int]
    reports: list[ReportNote]
    # The flag the library has now; None once the question was kept or replaced since.
    flag: QualityFlag | None = None


class KeyCheck(BaseModel):
    correct_index: int | None = Field(
        description="The number of the one option that is correct, or null when none of them "
        "is correct or more than one could be defended as correct."
    )
