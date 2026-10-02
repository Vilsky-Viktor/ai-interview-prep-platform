import asyncio
import uuid

import pytest
from prepza_common.user import User

from app.models.rounds import Answer, Round
from app.services import finish
from app.storage import certificates, progress, rounds

USER = User(uid="u1", email="u1@example.com", email_verified=True, name="Ann")
Q1, Q2 = uuid.uuid4(), uuid.uuid4()


def finishing_round(status: str = "in_progress") -> Round:
    return Round(
        id=uuid.uuid4(),
        topic_id=uuid.uuid4(),
        topic_title="Python",
        status=status,
        questions=[{"id": str(Q1)}, {"id": str(Q2)}],
        answers=[Answer(question_id=Q1, option_index=0, correct=True, score=100)],
    )


@pytest.fixture
def saved(monkeypatch):
    calls = {"finish": [], "rebuild": []}

    async def fake_finish(round_id, final, certificate):
        calls["finish"].append((final, certificate))

    async def fake_rebuild(user_id, question_ids):
        calls["rebuild"].append(question_ids)

    monkeypatch.setattr(rounds, "finish", fake_finish)
    monkeypatch.setattr(progress, "rebuild", fake_rebuild)

    return calls


def setup(monkeypatch, coverage, has_certificate=False):
    async def fake_coverage(round_, user_id):
        return coverage

    async def fake_has(user_id, topic_id):
        return has_certificate

    monkeypatch.setattr(finish, "topic_coverage", fake_coverage)
    monkeypatch.setattr(certificates, "has_for_topic", fake_has)


def test_first_full_topic_at_70_percent_earns_the_certificate(monkeypatch, saved):
    setup(monkeypatch, coverage=70)
    asyncio.run(finish.finish_round(finishing_round(), USER))

    (final, certificate), = saved["finish"]
    assert final == 50
    assert certificate.score == 70
    assert certificate.user_name == "Ann"
    assert saved["rebuild"] == [[Q1]]


def test_below_70_percent_or_incomplete_earns_nothing(monkeypatch, saved):
    for coverage in (69, None):
        setup(monkeypatch, coverage=coverage)
        asyncio.run(finish.finish_round(finishing_round(), USER))

    assert [certificate for _, certificate in saved["finish"]] == [None, None]


def test_certificate_is_issued_once_per_topic(monkeypatch, saved):
    setup(monkeypatch, coverage=100, has_certificate=True)
    asyncio.run(finish.finish_round(finishing_round(), USER))

    assert saved["finish"][0][1] is None


def test_finished_round_is_left_alone(monkeypatch, saved):
    setup(monkeypatch, coverage=100)
    asyncio.run(finish.finish_round(finishing_round("finished"), USER))

    assert saved == {"finish": [], "rebuild": []}
