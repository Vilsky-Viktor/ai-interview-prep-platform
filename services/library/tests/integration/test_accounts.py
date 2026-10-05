from app.storage import accounts, feedback
from tests.integration.factories import interview, question_ids


def test_deleting_a_user_removes_their_votes_and_reports_and_the_export_has_them(run):
    async def scenario():
        set_id = await interview("Ledgers")
        first, second, _ = await question_ids(set_id)
        await feedback.rate_question(first, "gone", -1)
        await feedback.report_question(second, "gone", "unclear", "Two answers fit.")
        await feedback.rate_question(first, "stays", 1)
        exported = await accounts.export("gone")

        await accounts.delete_user("gone")
        # Safe to repeat: a retried deletion finds nothing left.
        await accounts.delete_user("gone")

        return (
            exported,
            await feedback.my_question_rating(first, "gone"),
            await feedback.has_reported(second, "gone"),
            await feedback.my_question_rating(first, "stays"),
        )

    exported, vote, reported, kept = run(scenario())

    assert exported["question_votes"] == [{"question": "Ledgers question 0?", "vote": -1}]
    [report] = exported["question_reports"]
    assert (report["question"], report["reason"]) == ("Ledgers question 1?", "unclear")
    assert (vote, reported, kept) == (None, False, 1)
