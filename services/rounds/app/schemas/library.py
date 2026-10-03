from uuid import UUID

from pydantic import BaseModel


class Option(BaseModel):
    answer: str
    correct: bool


class Question(BaseModel):
    id: UUID
    text: str
    options: list[Option]


class TopicQuestions(BaseModel):
    id: UUID
    preparation_id: UUID
    title: str
    questions: list[Question]
    # Set for a topic in someone else's public kit: its certificate is paid, and starting it
    # counts towards the daily limit on new public topics.
    public_author_id: str | None = None
