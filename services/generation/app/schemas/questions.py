from pydantic import BaseModel, Field

from app.constants.generation import DISTRACTORS


class QuestionList(BaseModel):
    questions: list[str] = Field(description="Distinct interview questions, without numbering.")


class NewQuestion(BaseModel):
    question: str = Field(description="One new interview question, without numbering.")


class AnswerItem(BaseModel):
    id: int = Field(description="The id of the question being answered, copied exactly.")
    answer: str = Field(
        description="Correct, concise model answer (3-5 sentences) a strong candidate would give."
    )
    correct_option: str = Field(
        description="The correct answer condensed into ONE short sentence, usable as a "
        "multiple-choice option."
    )
    distractors: list[str] = Field(
        description=f"Exactly {DISTRACTORS} plausible but incorrect options, similar in "
        "length and style to correct_option."
    )


class AnswerList(BaseModel):
    answers: list[AnswerItem] = Field(description="One item per question id provided.")
