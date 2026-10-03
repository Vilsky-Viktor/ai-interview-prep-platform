import random

from app.constants.rounds import RoundStatus
from app.helpers.scores import current_score, score_passed
from app.models.rounds import Round
from app.schemas.library import TopicQuestions
from app.schemas.rounds import NextQuestion, RoundOut


def round_questions(topic: TopicQuestions, latest: dict[str, int]) -> list[dict]:
    """Every question of the topic: unanswered first, then the lowest latest scores; ties shuffled."""
    questions = [question.model_dump(mode="json") for question in topic.questions]
    random.shuffle(questions)
    questions.sort(key=lambda question: (question["id"] in latest, latest.get(question["id"], 0)))

    return questions


def next_question(round_) -> NextQuestion | None:
    answered = {str(answer.question_id) for answer in round_.answers}

    for number, question in enumerate(round_.questions, start=1):
        if question["id"] not in answered:
            return NextQuestion(
                question_id=question["id"],
                number=number,
                text=question["text"],
                options=[option["answer"] for option in question["options"]],
            )

    return None


def find_question(round_: Round, question_id: str) -> dict | None:
    return next((q for q in round_.questions if q["id"] == question_id), None)


def correct_option_index(question: dict) -> int:
    return next(i for i, option in enumerate(question["options"]) if option["correct"])


def round_out(round_: Round) -> RoundOut:
    return RoundOut(
        id=round_.id,
        topic_id=round_.topic_id,
        preparation_id=round_.preparation_id,
        topic_title=round_.topic_title,
        public_kit=round_.public_author_id is not None,
        status=round_.status,
        total=len(round_.questions),
        answered=len(round_.answers),
        current_score=current_score([answer.score for answer in round_.answers]),
        final_score=round_.final_score,
        passed=score_passed(
            round_.final_score
            if round_.status == RoundStatus.FINISHED
            else current_score([answer.score for answer in round_.answers])
        ),
        started_at=round_.started_at,
        finished_at=round_.finished_at,
        certificate_id=round_.certificate.id if round_.certificate else None,
    )
