from sqlalchemy import select

from app.models.feedback import PreparationRating
from app.models.sets import QuestionSet
from app.storage import accounts, feedback, joins, shares
from app.storage.db import Session
from tests.integration.factories import preparation


def test_deleting_a_user_removes_their_traces_and_recounts_ratings(run):
    async def scenario():
        own = await preparation("Mine")
        theirs = await preparation("Theirs")
        await joins.join(theirs, "gone")
        await feedback.rate_preparation(theirs, "gone", 5)
        await feedback.rate_preparation(theirs, "stays", 3)
        await shares.upsert(theirs, "gone@example.com", "owner", "Theirs", "Owner", "en")
        owned = await accounts.owned_preparations("owner")
        exported = await accounts.export("gone", "gone@example.com")

        await accounts.delete_user("gone", "Gone@Example.com")

        async with Session() as session:
            ratings = list(
                await session.scalars(
                    select(PreparationRating.user_id).where(PreparationRating.set_id == theirs)
                )
            )
            counts = (
                await session.execute(
                    select(
                        QuestionSet.rating_sum, QuestionSet.rating_count, QuestionSet.join_count
                    ).where(QuestionSet.id == theirs)
                )
            ).one()

        return own, owned, exported, ratings, tuple(counts), await joins.is_joined(theirs, "gone")

    own, owned, exported, ratings, counts, still_joined = run(scenario())

    assert own in owned
    assert [item["title"] for item in exported["joined_preparations"]] == ["Theirs"]
    assert [item["stars"] for item in exported["preparation_ratings"]] == [5]
    assert ratings == ["stays"]
    # Only the remaining rating counts; the owner's own join stays.
    assert counts[:2] == (3, 1)
    assert still_joined is False


def test_the_export_holds_owned_preparations_in_full(run):
    async def scenario():
        await preparation("Exported", topic="Ledgers", owner="exporter")

        return await accounts.export("exporter", "exporter@example.com")

    exported = run(scenario())
    [own] = exported["own_preparations"]
    [topic] = own["topics"]

    assert own["title"] == "Exported"
    assert own["pasted_text"] == "job text"
    assert topic["title"] == "Ledgers"
    assert topic["questions"][0] == {
        "question": "Exported question 0?",
        "options": [
            {"answer": "right", "correct": True},
            {"answer": "wrong", "correct": False},
        ],
    }
