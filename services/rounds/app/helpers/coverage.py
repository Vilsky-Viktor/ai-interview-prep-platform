from app.models.progress import QuestionProgress
from app.models.rounds import Round
from app.schemas.library import TopicQuestions


def topic_texts(topic: TopicQuestions) -> dict[str, str]:
    return {str(question.id): question.text for question in topic.questions}


def current_scores(rows: list[QuestionProgress], texts: dict[str, str]) -> dict[str, int]:
    """Latest score per current question; answers to a question since re-generated don't count."""
    return {
        str(row.question_id): row.score
        for row in rows
        if texts.get(str(row.question_id)) == row.question_text
    }


def with_round(latest: dict[str, int], round_: Round, texts: dict[str, str]) -> dict[str, int]:
    """Adds the answers of a round that is finishing now; they are the newest."""
    asked = {question["id"]: question["text"] for question in round_.questions}
    merged = dict(latest)

    for answer in round_.answers:
        question_id = str(answer.question_id)

        if question_id in texts and asked.get(question_id) == texts[question_id]:
            merged[question_id] = answer.score

    return merged


def coverage_score(latest: dict[str, int], texts: dict[str, str]) -> int | None:
    """Average over every question of the topic, or None until each one is answered."""
    if not texts or len(latest) < len(texts):
        return None

    return round(sum(latest.values()) / len(latest))
