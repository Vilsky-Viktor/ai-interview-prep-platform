from app.models.rounds import Answer


def learner_answer(question: dict, answer: Answer) -> str:
    return question["options"][answer.option_index]["answer"]


def correct_answer(question: dict) -> str:
    return next(option["answer"] for option in question["options"] if option["correct"])


def result_summary(answer: Answer) -> str:
    return f"Result: {'correct' if answer.correct else 'incorrect'}."
