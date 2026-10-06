import asyncio
import uuid
from types import SimpleNamespace

import pytest

from app.constants.invites import InviteStatus
from app.integrations import rounds
from app.services import candidate_results
from app.storage import candidates

FINISHED_ID = uuid.uuid4()
RUNNING_ID = uuid.uuid4()


@pytest.fixture
def saved(monkeypatch):
    """The results stored, by invite id."""
    rows = {}

    async def fake_save(results):
        rows.update(results)

    monkeypatch.setattr(candidates, "save_results", fake_save)

    return rows


def test_a_stored_grade_rounds_now_scores_differently_is_overwritten(saved):
    stale = SimpleNamespace(id=FINISHED_ID, status=InviteStatus.FINISHED, grade=50, flagged=False)
    current = SimpleNamespace(id=RUNNING_ID, status=InviteStatus.FINISHED, grade=80, flagged=False)
    totals = {
        str(FINISHED_ID): {"grade": 100, "finished": True},
        str(RUNNING_ID): {"grade": 80, "finished": True},
    }

    asyncio.run(candidate_results.sync([stale, current], totals))

    # An answer key was corrected since the first was stored; the second is already right.
    assert saved == {FINISHED_ID: (100, False)}
    assert stale.grade == 100


def test_rescored_candidates_get_their_new_grades_stored(saved, monkeypatch):
    async def fake_scores(invite_ids):
        return {
            str(FINISHED_ID): {"grade": 75, "finished": True},
            str(RUNNING_ID): {"grade": 40, "finished": False},
        }

    monkeypatch.setattr(rounds, "invite_scores", fake_scores)
    data = {"candidate_invite_ids": [str(FINISHED_ID), str(RUNNING_ID)]}

    asyncio.run(candidate_results.handle("results.rescored", data))
    asyncio.run(candidate_results.handle("interview.finished", data))

    # Only finished candidates have a stored grade; other events aren't this handler's.
    assert saved == {FINISHED_ID: (75, False)}
