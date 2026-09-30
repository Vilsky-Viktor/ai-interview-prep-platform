from uuid import UUID

from pydantic import BaseModel


class Option(BaseModel):
    answer: str
    correct: bool


class Question(BaseModel):
    id: UUID
    text: str
    reference_answer: str
    options: list[Option]


class TopicQuestions(BaseModel):
    id: UUID
    preparation_id: UUID
    title: str
    question_limit: int | None = None
    questions: list[Question]
