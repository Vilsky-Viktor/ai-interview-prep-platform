import uuid
from datetime import UTC, datetime, timedelta

from app.constants.reuse import MIN_REUSE_ANSWERS, RETIRE_AFTER_ANSWERS
from app.storage import bank, preparations, quality, reuse, templates
from tests.integration.factories import direction, interview


def test_templates_are_searched_and_filtered_and_keep_their_embeddings(run):
    word = uuid.uuid4().hex[:8]

    async def scenario():
        accountant = await interview(
            f"Senior accountant {word}", level="hard", template=True, embedding=direction(1)
        )
        await interview(f"Nurse {word}", level="basic", language="de", template=True)
        await interview(f"Company accountant {word}", level="hard")
        # A typed % is a percent sign, not a wildcard.
        await interview(f"100% {word}", template=True)

        def titles(rows):
            return [row.title for row in rows]

        return (
            titles(await templates.list_templates(word, None, [], 0, 10)),
            titles(await templates.list_templates(f"accountant {word}", "hard", ["en"], 0, 10)),
            titles(await templates.list_templates(word, None, ["de"], 0, 10)),
            titles(await templates.list_templates("0%", None, [], 0, 10)),
            await preparations.get_topics(accountant),
        )

    every, hard, german, percent, topics = run(scenario())

    assert sorted(every) == sorted([f"Senior accountant {word}", f"Nurse {word}", f"100% {word}"])
    assert hard == [f"Senior accountant {word}"]
    assert german == [f"Nurse {word}"]
    assert f"100% {word}" in percent
    assert len(topics) == 1


def test_templates_are_found_by_a_topic_or_a_subtopic_too(run):
    word = uuid.uuid4().hex[:8]

    async def scenario():
        await interview(
            "Platform engineer",
            topic=f"Kubernetes {word}",
            subtopics=[f"Helm charts {word}x"],
            template=True,
        )

        def titles(rows):
            return [row.title for row in rows]

        return (
            titles(await templates.list_templates(f"kubernetes {word}", None, [], 0, 10)),
            titles(await templates.list_templates(f"helm charts {word}x", None, [], 0, 10)),
        )

    by_topic, by_subtopic = run(scenario())

    assert by_topic == ["Platform engineer"]
    assert by_subtopic == ["Platform engineer"]


def test_a_template_is_copied_into_a_company_test_and_stays_a_template(run):
    async def scenario():
        template = await interview("Bookkeeper", template=True, questions=4)
        copy = await templates.copy_template(template, "company-9")
        missing = await templates.copy_template(copy.id, "company-9")

        return (
            await preparations.get(template),
            await preparations.get(copy.id),
            await preparations.get_topics(copy.id),
            missing,
        )

    template, copy, topics, missing = run(scenario())

    assert template.kind == "template"
    assert (copy.kind, copy.owner_type, copy.owner_id) == ("interview", "company", "company-9")
    assert copy.title == "Bookkeeper"
    # Of the template's 4 questions, the third went straight to practice: 3 private ones copied.
    assert [count for _, count in topics] == [3]
    # A company's test isn't a template, so it can't be copied in turn.
    assert missing is None


def test_a_template_reveals_a_third_and_its_copies_remember_their_originals(run):
    async def scenario():
        template = await interview("Nurse", template=True, questions=6)
        copy = await templates.copy_template(template, "company-3")
        original = await preparations.get_content(template)
        copied = await preparations.get_content(copy.id)

        return original.topics[0].questions, copied.topics[0].questions

    original, copied = run(scenario())

    assert [question.stage for question in original] == [
        "private",
        "private",
        "revealed",
        "private",
        "private",
        "revealed",
    ]
    private = [question.id for question in original if question.stage == "private"]
    assert [question.source_question_id for question in copied] == private


def test_the_bank_offers_only_proven_private_template_questions(run):
    async def scenario():
        template = await interview(
            "Bank accountant", level="hard", template=True, questions=3, embedding=direction(1)
        )
        # A company test on the same subject isn't part of the bank.
        await interview("Company accountant", level="hard", questions=3, embedding=direction(1))
        content = await preparations.get_content(template)
        private, unproven, revealed = content.topics[0].questions

        for question in (private, revealed):
            for _ in range(MIN_REUSE_ANSWERS):
                await quality.record_answer(question.id, question.text, "right", True)

        found = await reuse.find(direction(1), "hard", "en", 10)

        return found, private.id, unproven.id, revealed.id

    found, private, unproven, revealed = run(scenario())
    ids = [question_id for question_id, _, _ in found]

    assert private in ids
    assert unproven not in ids and revealed not in ids


def test_bank_questions_retire_after_enough_answers_and_are_revealed_once_idle(run):
    async def scenario():
        template = await interview("Electrician", template=True, questions=2)
        busy, quiet = (await preparations.get_content(template)).topics[0].questions
        # One company's test has a copy of each.
        await templates.copy_template(template, "company-7")

        for question in (busy, quiet):
            for _ in range(RETIRE_AFTER_ANSWERS):
                await quality.record_answer(question.id, question.text, "right", True)

        now = datetime.now(UTC)
        # Both have served enough candidates; the copies were used just now.
        first = await bank.move_stages(now - timedelta(days=90))
        after_first = await preparations.get_content(template)
        # As if 90 quiet days had passed: no copy used since.
        second = await bank.move_stages(now + timedelta(seconds=1))
        after_second = await preparations.get_content(template)

        return (
            first,
            [q.stage for q in after_first.topics[0].questions],
            second,
            [q.stage for q in after_second.topics[0].questions],
        )

    first, stages_first, second, stages_second = run(scenario())

    assert stages_first == ["retiring", "retiring"]
    assert stages_second == ["revealed", "revealed"]
    assert first[0] >= 2 and second[1] >= 2


def test_finished_topics_count_strong_weak_and_timeouts_for_copies_and_originals(run):
    from app.services.answer_events import handle

    async def scenario():
        template = await interview("Chemist", template=True, questions=2)
        copy = await templates.copy_template(template, "company-8")
        question = (await preparations.get_content(copy.id)).topics[0].questions[0]
        result = {
            "question_id": str(question.id),
            "question_text": question.text,
            "correct": True,
            "timed_out": False,
        }
        await handle("session.scored", {"final_score": 90, "answers": [result]})
        await handle(
            "session.scored",
            {"final_score": 20, "answers": [result | {"correct": False, "timed_out": True}]},
        )

        _, copy_stats, *_ = await quality.load(question.id)
        _, original_stats, *_ = await quality.load(question.source_question_id)

        return copy_stats, original_stats

    copy_stats, original_stats = run(scenario())

    for stats in (copy_stats, original_stats):
        assert (stats.strong_answers, stats.strong_correct) == (1, 1)
        assert (stats.weak_answers, stats.weak_correct) == (1, 0)
        assert stats.timeouts == 1


def test_a_new_template_never_reveals_questions_reused_from_the_bank(run):
    from prepza_common.sets import PreparationIn
    from sqlalchemy import select

    from app.constants.sets import Stage
    from app.models.sets import Question, Topic
    from app.storage.db import Session

    async def questions_of(set_id):
        async with Session() as session:
            rows = await session.scalars(
                select(Question)
                .join(Topic, Topic.id == Question.topic_id)
                .where(Topic.set_id == set_id)
                .order_by(Question.position)
            )

            return list(rows)

    async def scenario():
        older = await interview("Older template", template=True, questions=6)
        private = [row for row in await questions_of(older) if row.stage == Stage.PRIVATE]
        option = [{"answer": "right", "correct": True}, {"answer": "wrong", "correct": False}]
        reused = [
            {"text": row.text, "options": option, "source_id": str(row.id)} for row in private[:3]
        ]
        fresh = [{"text": f"New question {index}?", "options": option} for index in range(3)]
        newer = await templates.create_template(
            PreparationIn.model_validate(
                {
                    "generation_id": str(uuid.uuid4()),
                    "owner_uid": "prepza",
                    "source_text": "job text",
                    "title": "Newer template",
                    "level": "mid",
                    "language": "en",
                    "requirements": [],
                    "topics": [{"title": "Python", "subtopics": [], "questions": reused + fresh}],
                }
            )
        )

        return await questions_of(newer)

    rows = run(scenario())
    revealed = [row for row in rows if row.stage == Stage.REVEALED]

    # A third of its own new questions go to practice; the reused ones stay private.
    assert [row.source_question_id for row in revealed] == [None]
    assert all(row.stage == Stage.PRIVATE for row in rows if row.source_question_id)
