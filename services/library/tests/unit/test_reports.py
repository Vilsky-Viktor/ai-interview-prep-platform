import uuid

import pytest

from app.storage import feedback
from tests.unit.fake_redis import FakeRedis
from tests.unit.test_internal import token

QUESTION_ID = uuid.uuid4()
AUTH = {"Authorization": f"Bearer {token()}"}


@pytest.fixture(autouse=True)
def redis(monkeypatch):
    """Rate limits count in memory."""
    fake = FakeRedis()
    monkeypatch.setattr("app.routers.internal_feedback.get_redis", lambda: fake)

    return fake


def test_a_candidates_second_report_is_rejected(client, monkeypatch):
    reported = set()

    async def fake_report(question_id, user_id, reason, comment):
        if (question_id, user_id) in reported:
            return False

        reported.add((question_id, user_id))

        return True

    async def fake_has_reported(question_id, user_id):
        return (question_id, user_id) in reported

    async def fake_review(question_id):
        pass

    monkeypatch.setattr(feedback, "report_question", fake_report)
    monkeypatch.setattr(feedback, "has_reported", fake_has_reported)
    monkeypatch.setattr("app.routers.internal_feedback.review", fake_review)
    url = f"/internal/questions/{QUESTION_ID}/reports"
    body = {"user_id": "ann", "reason": "unclear"}

    assert client.get(f"{url}/mine", params={"user_id": "ann"}, headers=AUTH).json() == {
        "reported": False
    }
    assert client.post(url, json=body, headers=AUTH).status_code == 201
    assert client.post(url, json=body, headers=AUTH).status_code == 409
    assert client.get(f"{url}/mine", params={"user_id": "ann"}, headers=AUTH).json() == {
        "reported": True
    }


def test_a_users_reports_are_limited_a_day(client, monkeypatch):
    from app.constants.feedback import REPORTS_PER_DAY

    async def fake_report(question_id, user_id, reason, comment):
        return True

    async def fake_review(question_id):
        pass

    monkeypatch.setattr(feedback, "report_question", fake_report)
    monkeypatch.setattr("app.routers.internal_feedback.review", fake_review)
    body = {"user_id": "spammer", "reason": "unclear"}

    for _ in range(REPORTS_PER_DAY):
        url = f"/internal/questions/{uuid.uuid4()}/reports"
        assert client.post(url, json=body, headers=AUTH).status_code == 201

    url = f"/internal/questions/{uuid.uuid4()}/reports"
    assert client.post(url, json=body, headers=AUTH).status_code == 429
