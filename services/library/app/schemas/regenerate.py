from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.preparations import OptionIn


class QuestionContext(BaseModel):
    """What the generator needs to replace a question without repeating its topic."""

    set_id: UUID
    kind: str
    owner_id: str
    level: str
    topic: str
    subtopics: list[str]
    existing: list[str]


class QuestionReplace(BaseModel):
    text: str = Field(min_length=1)
    reference_answer: str = Field(min_length=1)
    options: list[OptionIn]
