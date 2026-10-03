from pydantic import BaseModel, Field, model_validator

from app.constants.help import (
    LAST_NOT_QUESTION,
    MAX_HELP_MESSAGE_LENGTH,
    MAX_HELP_MESSAGES,
    MAX_HELP_QUESTION_LENGTH,
    QUESTION_TOO_LONG,
    HelpRole,
)


class HelpMessage(BaseModel):
    role: HelpRole
    content: str = Field(min_length=1, max_length=MAX_HELP_MESSAGE_LENGTH)


class HelpChatRequest(BaseModel):
    """The conversation so far, ending with the new question; the page keeps it."""

    messages: list[HelpMessage] = Field(min_length=1, max_length=MAX_HELP_MESSAGES)

    @model_validator(mode="after")
    def ends_with_question(self):
        question = self.messages[-1]

        if question.role != HelpRole.USER:
            raise ValueError(LAST_NOT_QUESTION)

        if len(question.content) > MAX_HELP_QUESTION_LENGTH:
            raise ValueError(QUESTION_TOO_LONG)

        return self


class FaqItemOut(BaseModel):
    key: str
    question: str
    answer: str


class LegalSectionOut(BaseModel):
    heading: str
    paragraphs: list[str] = []
    items: list[str] = []


class LegalOut(BaseModel):
    intro: str
    updated: str
    sections: list[LegalSectionOut]
