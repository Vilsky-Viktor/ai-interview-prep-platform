from app.models.sets import Question
from app.schemas.preparations import QuestionText
from app.storage import feedback


async def question_texts(questions: list[Question]) -> list[QuestionText]:
    """Question text with feedback counts, without answers."""
    stats = await feedback.question_stats([question.id for question in questions])

    return [
        QuestionText(id=question.id, text=question.text, **stats.get(question.id, {}))
        for question in questions
    ]

