from prepza_common.constants import CHAT_FREE_TURNS

from app.constants.rounds import ChatRole
from app.models.rounds import Answer


def learner_answer(question: dict, answer: Answer) -> str:
    return question["options"][answer.option_index]["answer"]


def correct_answer(question: dict) -> str:
    return next(option["answer"] for option in question["options"] if option["correct"])


def result_summary(answer: Answer) -> str:
    return f"Result: {'correct' if answer.correct else 'incorrect'}."


def user_turns(history: list) -> int:
    return sum(1 for item in history if item.role == ChatRole.USER)


def free_turns_left(history: list) -> int:
    return max(0, CHAT_FREE_TURNS - user_turns(history))
