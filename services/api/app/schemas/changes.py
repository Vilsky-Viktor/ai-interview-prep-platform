from typing import Literal

from prepza_common.constants import MAX_GOAL_LENGTH
from prepza_common.user import Language
from pydantic import BaseModel, Field


class InterviewIn(BaseModel):
    job_description: str = Field(
        min_length=1,
        max_length=MAX_GOAL_LENGTH,
        description=(
            f"The job description to make the interview from, at most {MAX_GOAL_LENGTH} characters"
        ),
    )
    language: Language | None = Field(
        default=None,
        description=(
            "The language to write the interview in, as a code such as `en` or `de`; by "
            "default the job description's own"
        ),
    )


class CandidateUpdate(BaseModel):
    """Only the fields given change."""

    name: str | None = Field(
        default=None,
        max_length=200,
        description="The candidate's name; an empty string makes it unknown",
    )
    extra_time: Literal[0, 25, 50, 100] | None = Field(
        default=None,
        description=(
            "Extra time on each question, in percent, for a candidate who needs it; only "
            "before they start (409 after)"
        ),
    )


class Credits(BaseModel):
    available: int = Field(description="Credits your company can spend now")
    reserved: int = Field(description="Credits set aside for candidates who haven't finished")
    candidates: int = Field(description="How many more candidates the available credits pay for")
    low: bool = Field(description="Whether the credits are running low")
