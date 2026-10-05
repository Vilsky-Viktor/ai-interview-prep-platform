import uuid

from app.storage import feedback
from tests.unit.test_internal import token

QUESTION_ID = uuid.uuid4()
AUTH = {"Authorization": f"Bearer {token()}"}


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
