import asyncio
import uuid
from types import SimpleNamespace

import pytest

from app.integrations import billing, library
from app.models.generation import Generation
from app.services import outbox as outbox_service
from app.services.pipeline import stream_graph
from app.storage import generations

SET_ID = uuid.uuid4()
COMPANY_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def no_charge(monkeypatch):
    async def charge(_generation_id):
        return None

    monkeypatch.setattr(billing, "charge_kit", charge)


class FinishedGraph:
    """A graph whose run already finished: no more updates, just the final state."""

    async def astream(self, graph_input, config, stream_mode):
        return
        yield

    async def aget_state(self, config):
        return SimpleNamespace(
            values={
                "title": "Bookkeeper interview",
                "level": "basic",
                "requirements": [],
                "final": [],
            }
        )


@pytest.fixture
def published(monkeypatch):
    """Events the pipeline saves with the generation's last update (the outbox)."""
    sent = []

    async def saved(_payload):
        return SET_ID

    async def update(generation_id, event=None, **values):
        if event:
            sent.append(event)

    async def nothing():
        return None

    async def not_cancelled(_generation_id):
        return False

    monkeypatch.setattr(outbox_service, "flush_quietly", nothing)
    monkeypatch.setattr(library, "create_interview", saved)
    monkeypatch.setattr(library, "create_preparation", saved)
    monkeypatch.setattr(generations, "update", update)
    monkeypatch.setattr(generations, "is_cancelled", not_cancelled)

    return sent


def run(kind):
    generation = Generation(
        id=uuid.uuid4(),
        kind=kind,
        owner_uid="alice",
        company_id=COMPANY_ID if kind == "interview" else None,
        text="Job description",
        progress=None,
    )
    asyncio.run(stream_graph(FinishedGraph(), generation, None, {}))

    return generation


def test_finished_interview_is_announced_to_companies(published):
    generation = run("interview")

    assert published == [
        (
            "generation.completed",
            {
                "generation_id": str(generation.id),
                "company_id": str(COMPANY_ID),
                "set_id": str(SET_ID),
                "title": "Bookkeeper interview",
            },
        )
    ]


def test_finished_preparation_is_not_announced(published):
    run("preparation")

    assert published == []
