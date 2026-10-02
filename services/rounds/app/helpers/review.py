from app.helpers.rounds import correct_option_index
from app.schemas.review import AnswerView, ReviewItem


def build_review(round_) -> list[ReviewItem]:
    """Every question of the round in order; answers are only revealed for answered ones."""
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
                correct_option_index=correct_option_index(question) if answer else None,
                answer=(
                    AnswerView(
                        answer_id=answer.id,
                        option_index=answer.option_index,
                        correct=answer.correct,
                    )
                    if answer
                    else None
                ),
            )
        )

    return items
