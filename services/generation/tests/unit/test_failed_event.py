import asyncio
import uuid

import pytest

from app.constants.generation import GENERATION_FAILED
from app.constants.kinds import GenerationKind
from app.constants.statuses import Status
from app.models.generation import Generation
from app.services import jobs
from app.services import outbox as outbox_service
from app.storage import generations


@pytest.fixture
def failing_run(monkeypatch):
    """A claimed generation whose pipeline fails; returns the updates saved and the flushes."""
    saved = []
    flushes = []

    async def claimed(_generation_id):
        return True

    async def broken(*args):
        raise RuntimeError("model down")

    async def update(generation_id, event=None, **values):
        saved.append((event, values))

        return True

    async def flush():
        flushes.append(True)

    monkeypatch.setattr(generations, "claim_run", claimed)
    monkeypatch.setattr(generations, "update", update)
    monkeypatch.setattr(jobs, "run_pipeline", broken)
    monkeypatch.setattr(outbox_service, "flush_quietly", flush)

    def run(kind):
        generation = Generation(id=uuid.uuid4(), kind=kind, owner_uid="ann", text="job")

        async def found(_generation_id):
            return generation

        monkeypatch.setattr(generations, "get", found)
        asyncio.run(jobs.run_generation(None, generation.id, None))

        return generation, saved, flushes

    return run


def test_a_failed_interview_generation_saves_the_event_for_companies(failing_run):
    generation, saved, flushes = failing_run(GenerationKind.INTERVIEW)

    assert saved == [
        (
            ("generation.failed", {"generation_id": str(generation.id)}),
            {"status": Status.FAILED, "error": GENERATION_FAILED},
        )
    ]
    assert flushes == [True]


def test_a_failed_template_generation_tells_nobody(failing_run):
    _generation, saved, _flushes = failing_run(GenerationKind.TEMPLATE)

    assert saved == [(None, {"status": Status.FAILED, "error": GENERATION_FAILED})]
