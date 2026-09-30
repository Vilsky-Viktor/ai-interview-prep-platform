from pydantic import BaseModel


class OptionIn(BaseModel):
    answer: str
    correct: bool


class QuestionIn(BaseModel):
    text: str
    reference_answer: str
    options: list[OptionIn]


class TopicIn(BaseModel):
    title: str
    subtopics: list[str]
    questions: list[QuestionIn]


class PreparationIn(BaseModel):
    owner_uid: str
    source_text: str
    title: str
    level: str
    requirements: list[str]
    topics: list[TopicIn]
