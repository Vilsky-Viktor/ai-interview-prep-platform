from prepza_common.user import User

from app.constants.rounds import RoundStatus
from app.helpers.coverage import coverage_score, current_scores, topic_texts, with_round
from app.helpers.scores import earns_certificate, final_score
from app.integrations import library
from app.models.certificates import Certificate
from app.models.rounds import Round
from app.storage import certificates, progress, rounds


async def topic_coverage(round_: Round, user_id: str) -> int | None:
    """Percent correct over the whole topic across the user's rounds, this one included."""
    topic = await library.get_topic_questions(round_.topic_id, user_id)

    if topic is None:
        return None

    texts = topic_texts(topic)
    rows = await progress.for_topic(user_id, round_.topic_id)

    return coverage_score(with_round(current_scores(rows, texts), round_, texts), texts)


async def finish_round(round_: Round, user: User) -> None:
    """Scores the round and issues the topic's certificate once the user first earns it."""
    if round_.status == RoundStatus.FINISHED:
        return

    final = final_score([answer.score for answer in round_.answers], len(round_.questions))
    certificate = None
    coverage = await topic_coverage(round_, user.uid)

    if earns_certificate(coverage) and not await certificates.has_for_topic(
        user.uid, round_.topic_id
    ):
        certificate = Certificate(
            user_id=user.uid,
            user_name=user.name or user.email,
            round_id=round_.id,
            preparation_id=round_.preparation_id,
            topic_id=round_.topic_id,
            topic_title=round_.topic_title,
            score=coverage,
        )

    await rounds.finish(round_.id, final, certificate)
    await progress.rebuild(user.uid, [answer.question_id for answer in round_.answers])
