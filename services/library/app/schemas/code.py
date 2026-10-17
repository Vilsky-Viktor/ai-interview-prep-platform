import uuid

from pydantic import BaseModel, Field

from app.constants.code import CODE_LANGUAGE_PATTERN


class UntaggedQuestion(BaseModel):
    id: uuid.UUID
    text: str


class CodeLanguageIn(BaseModel):
    id: uuid.UUID
    language: str = Field(pattern=CODE_LANGUAGE_PATTERN)
