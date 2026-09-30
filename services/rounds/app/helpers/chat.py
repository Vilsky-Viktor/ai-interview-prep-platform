from app.models.rounds import Answer


def learner_answer(question: dict, answer: Answer) -> str:
    if answer.option_index is not None:
        return question["options"][answer.option_index]["answer"]

    return answer.text or ""


def grade_summary(answer: Answer) -> str:
    if answer.correct is not None:
        verdict = "correct" if answer.correct else "incorrect"

        return f"Result: {verdict} (multiple choice)."

    return f"Grade: {answer.score}/100. Grader feedback: {answer.feedback or 'none'}"
