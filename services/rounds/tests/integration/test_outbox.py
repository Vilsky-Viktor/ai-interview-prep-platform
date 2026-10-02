import uuid

from sqlalchemy import select

from app.models.outbox import OutboxEvent
from app.models.rounds import Answer
from app.storage import rounds
from app.storage.db import Session
from tests.integration.factories import option_index, topic


def test_an_answer_and_its_event_are_saved_together_and_a_repeat_saves_neither(run):
    async def scenario():
        round_ = await rounds.create("ann", topic(), {})
        question = round_.questions[0]
        event = ("answer.recorded", {"question_id": question["id"], "option": "right"})

        def answer():
            return Answer(
                round_id=round_.id,
                question_id=uuid.UUID(question["id"]),
                option_index=option_index(question, True),
                correct=True,
                score=100,
            )

        first = await rounds.add_answer(answer(), event)
        again = await rounds.add_answer(answer(), event)

        async with Session() as session:
            saved = list(
                await session.scalars(
                    select(OutboxEvent).where(
                        OutboxEvent.data["question_id"].astext == question["id"]
                    )
                )
            )

        return first, again, len(saved)

    first, again, saved = run(scenario())

    # The repeated answer was refused, and its event rolled back with it.
    assert (first, again, saved) == (True, False, 1)
