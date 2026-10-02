from app.constants.events import ANSWER_RECORDED
from app.services.answer_events import handle
from app.storage import quality
from tests.integration.factories import preparation, question_ids


def test_answer_events_build_question_statistics(run):
    async def scenario():
        [question_id, *_] = await question_ids(await preparation("Stats"))

        for option, correct in [("right", True), ("wrong", False), ("right", True)]:
            await handle(
                ANSWER_RECORDED,
                {
                    "question_id": str(question_id),
                    "question_text": "Stats question 0?",
                    "option": option,
                    "correct": correct,
                },
            )

        _, stats, *_ = await quality.load(question_id)

        return stats

    stats = run(scenario())

    assert (stats.answers, stats.correct) == (3, 2)
    assert stats.option_picks == {"right": 2, "wrong": 1}
