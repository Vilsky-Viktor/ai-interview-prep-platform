import uuid

from prepza_common.user import User

from app.integrations import library
from app.models.rounds import Answer
from app.services.finish import finish_round
from app.storage import certificates, progress, rounds
from tests.integration.factories import option_index, topic

USER = User(uid="ann", email="ann@example.com", email_verified=True, name="Ann")


async def answer_all(round_, correct):
    for question in round_.questions:
        await rounds.add_answer(
            Answer(
                round_id=round_.id,
                question_id=uuid.UUID(question["id"]),
                option_index=option_index(question, correct),
                correct=correct,
                score=100 if correct else 0,
            )
        )

    return await rounds.get(round_.id)


def test_progress_keeps_the_latest_answer_to_each_question(run):
    subject = topic()

    async def scenario():
        first = await answer_all(await rounds.create(USER.uid, subject, {}), correct=False)
        await progress.rebuild(USER.uid, [answer.question_id for answer in first.answers])
        second = await answer_all(await rounds.create(USER.uid, subject, {}), correct=True)
        await progress.rebuild(USER.uid, [answer.question_id for answer in second.answers])

        return await progress.for_topic(USER.uid, subject.id)

    rows = run(scenario())

    assert len(rows) == 3
    assert {row.score for row in rows} == {100}


def test_answering_the_whole_topic_right_earns_one_certificate(run, monkeypatch):
    subject = topic()

    async def fake_topic(topic_id, user_id):
        return subject

    monkeypatch.setattr(library, "get_topic_questions", fake_topic)

    async def scenario():
        round_ = await answer_all(await rounds.create(USER.uid, subject, {}), correct=True)
        await finish_round(round_, USER)
        # A second full round never issues a second certificate.
        again = await answer_all(await rounds.create(USER.uid, subject, {}), correct=True)
        await finish_round(again, USER)

        return (
            await certificates.for_preparation(USER.uid, subject.preparation_id),
            await rounds.get(round_.id),
        )

    issued, finished = run(scenario())

    assert list(issued) == [subject.id]
    assert finished.final_score == 100
