from app.storage import preparations, quality, quality_report
from tests.integration.factories import interview


def test_the_quality_tab_lists_flagged_and_replaced_questions(run):
    async def scenario():
        template = await interview("Quality template", template=True, questions=2)
        flagged, kept = (await preparations.get_content(template)).topics[0].questions
        await quality.record_answer(flagged.id, flagged.text, "right", True)
        await quality.save_flag(flagged.id, "wrong_key")
        await preparations.replace_question(
            kept.id, "A clearer question?", [{"answer": "Yes", "correct": True}]
        )

        return (
            await quality_report.flagged(0, 100),
            await quality_report.replaced(0, 100),
            flagged.id,
            kept,
        )

    flagged_rows, replaced_rows, flagged_id, kept = run(scenario())

    [row] = [row for row in flagged_rows if row[0].id == flagged_id]
    _, stats, question_set, reports = row
    assert (stats.flag, stats.answers, question_set.kind, reports) == (
        "wrong_key",
        1,
        "template",
        0,
    )

    [(revision, revised_set)] = [row for row in replaced_rows if row[0].question_id == kept.id]
    assert revision.text == kept.text
    assert revised_set.title == "Quality template"
