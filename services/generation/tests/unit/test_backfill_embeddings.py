import asyncio

from app.integrations import library, llm
from app.jobs.backfill_embeddings import backfill


class FakeEmbeddings:
    def __init__(self):
        self.texts = []

    async def aembed_documents(self, texts):
        self.texts.extend(texts)

        return [[float(len(self.texts))] for _ in texts]


def test_embeds_every_batch_until_nothing_is_missing(monkeypatch):
    batches = [
        [{"id": "t1", "title": "Bookkeeping", "subtopics": ["Cash", "Journals"]}],
        [{"id": "t2", "title": "SQL joins", "subtopics": []}],
        [],
    ]
    saved = {}
    embeddings = FakeEmbeddings()

    async def fake_missing(limit):
        return batches.pop(0)

    async def fake_save(items):
        saved.update(items)

    monkeypatch.setattr(library, "missing_embeddings", fake_missing)
    monkeypatch.setattr(library, "save_embeddings", fake_save)
    monkeypatch.setattr(llm, "get_embeddings", lambda: embeddings)

    assert asyncio.run(backfill()) == 2
    assert embeddings.texts == ["Bookkeeping: Cash, Journals", "SQL joins"]
    assert set(saved) == {"t1", "t2"}
