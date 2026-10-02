from pydantic import BaseModel, Field

from app.constants.generation import DISTRACTORS, MAX_OPTION_CHARS


class QuestionItem(BaseModel):
    question: str = Field(description="The question itself, without numbering or listed choices.")
    correct_option: str = Field(
        description="The correct answer, as concise as possible while complete and accurate, "
        f"never longer than {MAX_OPTION_CHARS} characters."
    )
    distractors: list[str] = Field(
        description=f"Exactly {DISTRACTORS} plausible but incorrect options, each at most "
        f"{MAX_OPTION_CHARS} characters, similar in length and style to correct_option."
    )
    ambiguous: bool = Field(
        description="True if more than one of the options could be defended as a correct "
        "answer to the question as written; the question is then dropped."
    )


class QuestionItemList(BaseModel):
    items: list[QuestionItem] = Field(description="Distinct questions, each with its options.")


class NewQuestion(BaseModel):
    question: str = Field(description="One new interview question, without numbering.")


class AnswerItem(BaseModel):
    id: int = Field(description="The id of the question being answered, copied exactly.")
    correct_option: str = Field(
        description="The correct answer, as concise as possible while complete and accurate, "
        f"never longer than {MAX_OPTION_CHARS} characters. Used as a multiple-choice option."
    )
    distractors: list[str] = Field(
        description=f"Exactly {DISTRACTORS} plausible but incorrect options, each at most "
        f"{MAX_OPTION_CHARS} characters, similar in "
        "length and style to correct_option."
    )
    ambiguous: bool = Field(
        description="True if more than one of the options could be defended as a correct "
        "answer to the question as written; the question is then dropped."
    )


class AnswerList(BaseModel):
    answers: list[AnswerItem] = Field(description="One item per question id provided.")
