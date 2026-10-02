import uuid
from datetime import UTC, datetime

from app.helpers.coverage import coverage_score, current_scores, with_round
from app.models.progress import QuestionProgress
from app.models.rounds import Answer, Round

Q1, Q2, Q3 = (str(uuid.uuid4()) for _ in range(3))
TEXTS = {Q1: "One?", Q2: "Two?", Q3: "Three?"}


def progress(scores: dict[str, int], texts: dict[str, str] = TEXTS) -> list[QuestionProgress]:
    return [
        QuestionProgress(
            question_id=uuid.UUID(question_id),
            question_text=texts[question_id],
            score=score,
            answered_at=datetime.now(UTC),
        )
        for question_id, score in scores.items()
    ]


def finishing_round(scores: dict[str, int]) -> Round:
    return Round(
        id=uuid.uuid4(),
        questions=[
            {"id": question_id, "text": TEXTS[question_id], "options": []}
            for question_id in scores
        ],
        answers=[
            Answer(question_id=uuid.UUID(question_id), score=score)
            for question_id, score in scores.items()
        ],
    )


def test_certificate_needs_every_question_across_rounds():
    earlier = current_scores(progress({Q1: 90, Q2: 60}), TEXTS)

    assert coverage_score(earlier, TEXTS) is None
    assert coverage_score(with_round(earlier, finishing_round({Q3: 80}), TEXTS), TEXTS) == 77


def test_finishing_round_is_the_latest_answer():
    earlier = current_scores(progress({Q1: 20, Q2: 80, Q3: 80}), TEXTS)

    assert with_round(earlier, finishing_round({Q1: 100}), TEXTS)[Q1] == 100


def test_regenerated_question_is_not_covered():
    latest = current_scores(progress({Q1: 90, Q2: 90, Q3: 90}, {**TEXTS, Q2: "Old two?"}), TEXTS)

    assert Q2 not in latest
    assert coverage_score(latest, TEXTS) is None
