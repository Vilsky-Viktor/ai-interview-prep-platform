from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.constants.generation import MAX_GOAL_LENGTH
from app.constants.kinds import GenerationKind
from app.constants.statuses import Status
from app.helpers.usage import cost_usd


class GenerationCreate(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_GOAL_LENGTH)
    kind: GenerationKind = GenerationKind.PREPARATION
    company_id: UUID | None = None

    @model_validator(mode="after")
    def interview_needs_company(self):
        if self.kind == GenerationKind.INTERVIEW and self.company_id is None:
            raise ValueError("company_id is required for an interview")

        if self.kind == GenerationKind.PREPARATION and self.company_id is not None:
            raise ValueError("company_id is only used for interviews")

        return self


class ReviewRequest(BaseModel):
    selected: list[int] = Field(min_length=1)
    instructions: str = ""


class GenerationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: GenerationKind
    company_id: UUID | None
    status: Status
    topics: list[dict] | None
    progress: dict | None
    preparation_id: UUID | None
    error: str | None
    usage: dict | None = None

    @computed_field
    @property
    def cost_usd(self) -> float | None:
        return cost_usd(self.usage)
