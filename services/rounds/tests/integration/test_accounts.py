import uuid

from app.models.certificates import Certificate
from app.models.rounds import Answer
from app.storage import accounts, certificates, progress, rounds, sessions
from tests.integration.factories import option_index, topic


def test_deleting_a_user_removes_rounds_progress_certificates_and_sessions(run):
    subject = topic()

    async def scenario():
        round_ = await rounds.create("gone", subject, {})
        question = round_.questions[0]
        await rounds.add_answer(
            Answer(
                round_id=round_.id,
                question_id=uuid.UUID(question["id"]),
                option_index=option_index(question, True),
                correct=True,
                score=100,
            ),
            ("answer.recorded", {"question_id": question["id"]}),
        )
        await progress.rebuild("gone", [uuid.UUID(question["id"])])
        certificate = Certificate(
            user_id="gone",
            user_name="Gone",
            round_id=round_.id,
            preparation_id=subject.preparation_id,
            topic_id=subject.id,
            topic_title="Python",
            score=100,
        )
        await rounds.finish(round_.id, 100, certificate)
        [session] = await sessions.create_many("gone", uuid.uuid4(), False, [topic()], None)
        kept = await rounds.create("stays", subject, {})
        exported = await accounts.export("gone")

        await accounts.delete_user("gone")
        # Safe to repeat: a retried deletion finds nothing left.
        await accounts.delete_user("gone")

        return (
            exported,
            await rounds.get(round_.id),
            await progress.for_topic("gone", subject.id),
            await certificates.get(certificate.id),
            await sessions.get(session.id),
            await rounds.get(kept.id),
        )

    exported, round_, progress_rows, certificate, session, kept = run(scenario())

    assert len(exported["practice_rounds"]) == 1
    assert len(exported["certificates"]) == 1
    assert len(exported["interview_sections"]) == 1
    assert (round_, progress_rows, certificate, session) == (None, [], None, None)
    assert kept is not None
