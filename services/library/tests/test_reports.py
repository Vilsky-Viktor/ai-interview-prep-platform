import uuid

from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.sets import SetKind, Visibility
from app.main import app
from app.models.sets import QuestionSet
from app.storage import feedback, preparations

QUESTION_ID = uuid.uuid4()


def test_second_report_is_rejected(client, monkeypatch):
    reported = set()

    async def fake_set(_question_id):
        return QuestionSet(
            id=uuid.uuid4(), kind=SetKind.PREPARATION, owner_id="ann", visibility=Visibility.PRIVATE
        )

    async def fake_report(question_id, user_id, reason, comment):
        if (question_id, user_id) in reported:
            return False

        reported.add((question_id, user_id))

        return True

    async def fake_has_reported(question_id, user_id):
        return (question_id, user_id) in reported

    monkeypatch.setattr(preparations, "get_for_question", fake_set)
    monkeypatch.setattr(feedback, "report_question", fake_report)
    monkeypatch.setattr(feedback, "has_reported", fake_has_reported)
    app.dependency_overrides[current_user] = lambda: User(
        uid="ann", email="ann@example.com", email_verified=True, name="Ann"
    )
    url = f"/questions/{QUESTION_ID}/reports"

    assert client.get(f"{url}/mine").json() == {"reported": False}
    assert client.post(url, json={"reason": "unclear"}).status_code == 201
    assert client.post(url, json={"reason": "unclear"}).status_code == 409
    assert client.get(f"{url}/mine").json() == {"reported": True}

    app.dependency_overrides.clear()
