from app.models.sets import QuestionSet


def preparation_export(question_set: QuestionSet) -> dict:
    """A preparation the user owns, in full, as their data export shows it."""
    return {
        "title": question_set.title,
        "visibility": question_set.visibility,
        "level": question_set.level,
        "language": question_set.language,
        "created_at": question_set.created_at,
        "pasted_text": question_set.source_text,
        "requirements": question_set.requirements,
        "topics": [
            {
                "title": topic.title,
                "subtopics": topic.subtopics,
                "questions": [
                    {
                        "question": question.text,
                        "options": [
                            {"answer": option["answer"], "correct": option["correct"]}
                            for option in question.options
                        ],
                    }
                    for question in topic.questions
                ],
            }
            for topic in question_set.topics
        ],
    }
