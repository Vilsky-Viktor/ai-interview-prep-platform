from uuid import UUID

from pydantic import BaseModel


class QuestionContext(BaseModel):
    set_id: UUID
    kind: str
    owner_id: str
    level: str
    topic: str
    subtopics: list[str]
    existing: list[str]


class RegenerateIn(BaseModel):
    user_id: str
    set_id: UUID


class RegeneratedOption(BaseModel):
    answer: str
    correct: bool


class RegeneratedQuestion(BaseModel):
    text: str
    reference_answer: str
    options: list[RegeneratedOption]


class RegeneratedOut(BaseModel):
    id: UUID
    text: str
