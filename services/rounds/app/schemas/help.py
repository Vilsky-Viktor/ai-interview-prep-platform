from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.constants.help import (
    LAST_NOT_QUESTION,
    MAX_HELP_MESSAGE_LENGTH,
    MAX_HELP_MESSAGES,
    MAX_HELP_QUESTION_LENGTH,
    QUESTION_TOO_LONG,
    SIGNATURE_LENGTH,
    HelpRole,
)


class HelpMessage(BaseModel):
    role: HelpRole
    content: str = Field(min_length=1, max_length=MAX_HELP_MESSAGE_LENGTH)
    # A reply's signature, as the help chat gave it when it wrote the reply.
    signature: str | None = Field(default=None, max_length=SIGNATURE_LENGTH)


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
    # The language of the text: the one asked for when it's translated, otherwise English.
    language: str
    intro: str
    # The day this text applies from, the newest version's, the one that applies today, and every
    # published one, newest first.
    version: str
    state: Literal["in_force", "upcoming", "replaced"]
    current: str
    in_force: str
    versions: list[str]
    sections: list[LegalSectionOut]
