import uuid

from app.schemas.library import TopicQuestions


def topic(size=3):
    """A topic whose questions all have option "right" as the correct one."""
    return TopicQuestions.model_validate(
        {
            "id": str(uuid.uuid4()),
            "preparation_id": str(uuid.uuid4()),
            "title": "Python",
            "questions": [
                {
                    "id": str(uuid.uuid4()),
                    "text": f"Question {index}?",
                    "options": [
                        {"answer": "right", "correct": True},
                        {"answer": "wrong", "correct": False},
                    ],
                }
                for index in range(size)
            ],
        }
    )


def option_index(question: dict, correct: bool) -> int:
    return next(i for i, option in enumerate(question["options"]) if option["correct"] == correct)
