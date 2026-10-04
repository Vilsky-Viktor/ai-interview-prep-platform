from pydantic import BaseModel, Field

from app.constants.generation import DISTRACTORS, MAX_OPTION_CHARS

EXAMPLE = (
    "The program, query, command, formula or file the question is about, exactly as it would be "
    "typed, with real line breaks and indentation and without a Markdown fence; for a query, the "
    "table's few rows first. Null when the question shows none. Never null when the question "
    'refers to one, such as "this query" or "the file below".'
)


class QuestionItem(BaseModel):
    question: str = Field(
        description="The question itself in plain sentences, without numbering, listed choices "
        "or the example."
    )
    example: str | None = Field(description=EXAMPLE)
    correct_option: str = Field(
        description="The correct answer, as concise as possible while complete and accurate, "
        f"never longer than {MAX_OPTION_CHARS} characters."
    )
    distractors: list[str] = Field(
        description=f"Exactly {DISTRACTORS} plausible but incorrect options, each at most "
        f"{MAX_OPTION_CHARS} characters, in the same form as correct_option and about as long "
        "as it, never noticeably shorter."
    )
    ambiguous: bool = Field(
        description="True if more than one of the options could be defended as a correct "
        "answer to the question as written; the question is then dropped."
    )


class QuestionItemList(BaseModel):
    items: list[QuestionItem] = Field(description="Distinct questions, each with its options.")


class NewQuestion(BaseModel):
    question: str = Field(
        description="One new interview question in plain sentences, without numbering or the "
        "example."
    )
    example: str | None = Field(description=EXAMPLE)


class AnswerItem(BaseModel):
    id: int = Field(description="The id of the question being answered, copied exactly.")
    correct_option: str = Field(
        description="The correct answer, as concise as possible while complete and accurate, "
        f"never longer than {MAX_OPTION_CHARS} characters. Used as a multiple-choice option."
    )
    distractors: list[str] = Field(
        description=f"Exactly {DISTRACTORS} plausible but incorrect options, each at most "
        f"{MAX_OPTION_CHARS} characters, in the same form as correct_option and about as long "
        "as it, never noticeably shorter."
    )
    ambiguous: bool = Field(
        description="True if more than one of the options could be defended as a correct "
        "answer to the question as written; the question is then dropped."
    )


class AnswerList(BaseModel):
    answers: list[AnswerItem] = Field(description="One item per question id provided.")
