import uuid

from app.storage import reuse
from tests.test_internal import token

OPTIONS = [{"answer": "Debit cash", "correct": True}, {"answer": "Credit cash", "correct": False}]


def find(client, body):
    return client.post("/internal/reuse", json=body, headers={"Authorization": f"Bearer {token()}"})


def test_proven_questions_are_offered_for_a_similar_topic(client, monkeypatch):
    asked = {}

    async def fake_find(embedding, level, count):
        asked.update(embedding=embedding, level=level, count=count)

        return [("A customer pays cash. Which entry is recorded?", OPTIONS)]

    monkeypatch.setattr(reuse, "find", fake_find)

    response = find(client, {"embedding": [0.1, 0.2], "level": "basic", "count": 5})

    assert response.status_code == 200
    assert response.json() == [
        {"text": "A customer pays cash. Which entry is recorded?", "options": OPTIONS}
    ]
    assert asked == {"embedding": [0.1, 0.2], "level": "basic", "count": 5}


def test_count_is_bounded(client):
    assert find(client, {"embedding": [0.1], "level": "basic", "count": 0}).status_code == 422
    assert find(client, {"embedding": [0.1], "level": "basic", "count": 101}).status_code == 422


def test_vectors_are_written_the_way_pgvector_reads_them():
    assert reuse.as_vector([0.5, -1.0, 2e-05]) == "[0.5,-1.0,2e-05]"


def test_backfill_lists_topics_and_saves_their_embeddings(client, monkeypatch):
    topic_id = uuid.uuid4()
    saved = {}

    async def fake_missing(limit):
        return [(topic_id, "Bookkeeping", ["Cash accounts"])]

    async def fake_save(embeddings):
        saved.update(embeddings)

    monkeypatch.setattr(reuse, "missing", fake_missing)
    monkeypatch.setattr(reuse, "save", fake_save)
    headers = {"Authorization": f"Bearer {token()}"}

    listed = client.get("/internal/embeddings/missing?limit=10", headers=headers)
    stored = client.put(
        "/internal/embeddings", json=[{"id": str(topic_id), "embedding": [0.1]}], headers=headers
    )

    assert listed.json() == [
        {"id": str(topic_id), "title": "Bookkeeping", "subtopics": ["Cash accounts"]}
    ]
    assert stored.status_code == 204
    assert saved == {topic_id: [0.1]}
