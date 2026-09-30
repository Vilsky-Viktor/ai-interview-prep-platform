from app.constants.rounds import Mode
from app.helpers.coverage import coverage_score, current_scores, topic_texts, with_round
from app.helpers.scores import earns_certificate, final_score
from app.integrations import library
from app.models.certificates import Certificate
from app.models.rounds import Round
from app.schemas.user import User
from app.storage import progress, rounds


async def topic_coverage(round_: Round, user_id: str) -> int | None:
    """Average over the whole topic across the user's open answer rounds, this one included."""
    topic = await library.get_topic_questions(round_.topic_id, user_id)

    if topic is None:
        return None

    texts = topic_texts(topic)
    rows = await progress.for_topic(user_id, round_.topic_id, Mode.OPEN)

    return coverage_score(with_round(current_scores(rows, texts), round_, texts), texts)


async def finish_round(round_: Round, user: User) -> None:
    total = len(round_.questions)
    answered = len(round_.answers)
    final = final_score(round_.mode, [answer.score for answer in round_.answers], total)
    certificate = None

    if round_.mode == Mode.OPEN and answered == total:
        coverage = await topic_coverage(round_, user.uid)

        if earns_certificate(round_.mode, answered, total, coverage):
            certificate = Certificate(
                user_id=user.uid,
                user_name=user.name or user.email,
                round_id=round_.id,
                topic_id=round_.topic_id,
                topic_title=round_.topic_title,
                score=coverage,
            )

    await rounds.finish(round_.id, final, certificate)
    await progress.rebuild(user.uid, [answer.question_id for answer in round_.answers])
