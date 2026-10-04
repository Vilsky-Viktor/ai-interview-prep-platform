import asyncio

import pytest

from app.config.settings import settings
from app.integrations import library, llm
from app.services.nodes.reuse import find_reused


class FakeEmbeddings:
    async def aembed_documents(self, texts):
        return [[1.0] for _ in texts]


@pytest.mark.parametrize(
    ("kind", "asked"),
    [
        # A learner's kit may be mostly proven questions; a company's interview stays mostly new.
        ("preparation", 56),
        ("interview", 35),
        # A run started before the kind was passed takes the smaller share.
        (None, 35),
    ],
)
def test_reuse_takes_a_bigger_share_of_a_learners_kit(monkeypatch, kind, asked):
    counts = []

    async def find(request):
        counts.append(request.count)

        return []

    monkeypatch.setattr(settings, "questions_per_topic", 70)
    monkeypatch.setattr(llm, "get_embeddings", FakeEmbeddings)
    monkeypatch.setattr(library, "find_reusable", find)
    state = {"topics": [{"main_topic": "SQL", "subtopics": []}], "level": "medium", "kind": kind}

    asyncio.run(find_reused(state))

    assert counts == [asked]
