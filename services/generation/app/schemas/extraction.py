from typing import Literal

from pydantic import BaseModel, Field


class JobExtraction(BaseModel):
    title: str = Field(
        description="Short title for this preparation (max 60 characters), for example the "
        "role and company, or the learning goal."
    )
    requirements: list[str] = Field(
        description="Concrete, distinct requirements/qualifications extracted from the text."
    )
    level: Literal["basic", "medium", "hard"] = Field(
        description="Level of complexity based on required seniority."
    )
