from prepza_common.user import Level
from pydantic import BaseModel, Field


class JobExtraction(BaseModel):
    title: str = Field(
        description="Short title for this test (max 60 characters), for example the role and "
        "company."
    )
    requirements: list[str] = Field(
        description="Concrete, distinct requirements/qualifications extracted from the text."
    )
    level: Level = Field(description="Level of complexity based on required seniority.")
