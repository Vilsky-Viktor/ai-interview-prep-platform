import asyncio
import uuid
from datetime import UTC, datetime

from prepza_common.auth import current_user
from prepza_common.constants import MAX_PAGE_SIZE
from prepza_common.user import User

from app.integrations import rounds
from app.main import app
from app.models.sets import QuestionSet
from app.services.done import done_ids
from app.storage import preparations, search


def test_library_search_is_public_and_paged(client, monkeypatch):
    asked = []

    async def fake_search(text, offset, limit):
        asked.append((text, offset, limit))

        return []

    monkeypatch.setattr(search, "search_public", fake_search)

    assert client.get("/library", params={"q": "python"}).status_code == 200
    assert client.get("/library", params={"offset": 20, "limit": 21}).status_code == 200
    assert client.get("/library", params={"limit": 500}).status_code == 422
    assert asked == [("python", 0, MAX_PAGE_SIZE), ("", 20, 21)]


def test_search_matches_title():
    compiled = str(search._matches("acme").compile()).lower()

    assert "like" in compiled
    assert "sets.title" in compiled


def test_my_preparations_mark_owned_ones_and_are_paged(client, monkeypatch):
    def row(owner):
        item = QuestionSet(
            id=uuid.uuid4(),
            title="T",
            level="basic",
            visibility="private",
            owner_id=owner,
            created_at=datetime.now(UTC),
            topic_count=1,
        )

        return item, 1, None, 0, 1

    asked = []

    async def fake_mine(user_id, offset, limit):
        asked.append((user_id, offset, limit))

        return [row("ann"), row("bob")]

    async def no_mastery(user_id, preparation_ids):
        return {}

    monkeypatch.setattr(preparations, "list_mine", fake_mine)
    monkeypatch.setattr(rounds, "mastered_counts", no_mastery)
    app.dependency_overrides[current_user] = lambda: User(
        uid="ann", email="ann@example.com", email_verified=True
    )
    response = client.get("/preparations", params={"offset": 20, "limit": 20})
    app.dependency_overrides.clear()

    assert [item["owned"] for item in response.json()] == [True, False]
    assert [item["done"] for item in response.json()] == [False, False]
    assert asked == [("ann", 20, 20)]


def test_a_preparation_is_done_once_every_topic_is_mastered(monkeypatch):
    finished, halfway, empty = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

    async def fake_counts(user_id, preparation_ids):
        return {str(finished): 3, str(halfway): 1}

    monkeypatch.setattr(rounds, "mastered_counts", fake_counts)

    done = asyncio.run(done_ids("ann", {finished: 3, halfway: 3, empty: 0}))

    assert done == {finished}


def test_without_rounds_nothing_is_done(monkeypatch):
    async def down(user_id, preparation_ids):
        raise ConnectionError("rounds is down")

    monkeypatch.setattr(rounds, "mastered_counts", down)

    assert asyncio.run(done_ids("ann", {uuid.uuid4(): 2})) == set()
