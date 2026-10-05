from app.constants.integrity import FAST_ANSWER_SECONDS, IntegritySignal
from app.helpers.rounds import correct_option_index
from app.schemas.review import AnswerView, ReviewItem


def add_signals(items: list[ReviewItem], signals: list) -> None:
    """Counts each question's page leaves and copy attempts into its review item."""
    by_question = {str(item.question_id): item for item in items}

    for signal in signals:
        item = by_question.get(str(signal.question_id))

        if item is None:
            continue

        if signal.kind == IntegritySignal.TAB_LEAVE:
            item.tab_leaves += 1
        else:
            item.copies += 1


def build_review(round_, reveal_all: bool = False) -> list[ReviewItem]:
    """Every question of the round in order; the right answer only for answered ones, or for
    every one with `reveal_all` (a practice round)."""
    answers = {str(answer.question_id): answer for answer in round_.answers}
    items = []

    for number, question in enumerate(round_.questions, start=1):
        answer = answers.get(question["id"])
        items.append(
            ReviewItem(
                question_id=question["id"],
                number=number,
                text=question["text"],
                options=[option["answer"] for option in question["options"]],
                correct_option_index=(
                    correct_option_index(question) if answer or reveal_all else None
                ),
                answer=(
                    AnswerView(
                        answer_id=answer.id,
                        option_index=answer.option_index,
                        correct=answer.correct,
                        seconds=answer.seconds,
                        fast=answer.option_index is not None
                        and answer.seconds is not None
                        and answer.seconds < FAST_ANSWER_SECONDS,
                    )
                    if answer
                    else None
                ),
            )
        )

    return items
