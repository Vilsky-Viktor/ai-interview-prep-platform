from app.constants.reuse import MIN_REUSE_ANSWERS
from app.storage import quality, reuse
from tests.integration.factories import direction, preparation, question_ids


async def prove(question_id, text):
    for _ in range(MIN_REUSE_ANSWERS):
        await quality.record_answer(question_id, text, "right", True)


def test_reuse_takes_proven_questions_from_close_public_topics_only(run):
    async def scenario():
        close = await preparation("Close", embedding=direction(1.0, 0.1))
        far = await preparation("Far", embedding=direction(0.0, 1.0))
        private = await preparation("Private", embedding=direction(1.0, 0.0), public=False)
        senior = await preparation("Senior", level="senior", embedding=direction(1.0, 0.0))

        for set_id, title in [
            (close, "Close"),
            (far, "Far"),
            (private, "Private"),
            (senior, "Senior"),
        ]:
            for index, question_id in enumerate(await question_ids(set_id)):
                await prove(question_id, f"{title} question {index}?")

        # One proven question is flagged, and one more is never answered enough.
        close_ids = await question_ids(close)
        await quality.save_flag(close_ids[0], "rewrite")
        unproven = await preparation("Unproven", embedding=direction(1.0, 0.05))

        found = await reuse.find(direction(1.0, 0.0), "mid", 10)

        return [text for text, _ in found], unproven

    texts, _ = run(scenario())

    assert sorted(texts) == ["Close question 1?", "Close question 2?"]
