from typing import Literal

from pydantic import BaseModel, Field


class JobExtraction(BaseModel):
    title: str = Field(
        description="Short title for this preparation (max 60 characters), for example the "
        "role and company, or the learning goal."
    )
    company_name: str = Field(
        description="Company name, if mentioned or reasonably inferable; empty string otherwise."
    )
    company_description: str = Field(
        default="",
        description="A description of what the company does, taken from the text. "
        "Empty string if the text does not describe the company itself.",
    )
    requirements: list[str] = Field(
        description="Concrete, distinct requirements/qualifications extracted from the text."
    )
    level: Literal["basic", "medium", "hard"] = Field(
        description="Level of complexity based on required seniority."
    )
