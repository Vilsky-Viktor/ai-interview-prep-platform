import uuid

from app.models.answers import Answer
from app.storage import accounts, sessions
from tests.integration.factories import option_index, topic


def test_deleting_a_user_removes_their_interview_sessions(run):
    async def scenario():
        [session] = await sessions.create_many("gone", uuid.uuid4(), [topic()], 60)
        question = session.questions[0]
        await sessions.add_answer(
            Answer(
                session_id=session.id,
                question_id=uuid.UUID(question["id"]),
                option_index=option_index(question, True),
                correct=True,
                score=100,
            ),
            ("answer.recorded", {"question_id": question["id"]}),
        )
        [kept] = await sessions.create_many("stays", uuid.uuid4(), [topic()], 60)
        exported = await accounts.export("gone")

        await accounts.delete_user("gone")
        # Safe to repeat: a retried deletion finds nothing left.
        await accounts.delete_user("gone")

        return exported, await sessions.get(session.id), await sessions.get(kept.id)

    exported, session, kept = run(scenario())

    [section] = exported["interview_sections"]
    [answer] = section["answers"]

    assert answer["your_answer"] == "right"
    # Whether a company interview's answer was right isn't the candidate's to see.
    assert "correct" not in answer
    assert section["final_score"] is None
    assert session is None
    assert kept is not None
