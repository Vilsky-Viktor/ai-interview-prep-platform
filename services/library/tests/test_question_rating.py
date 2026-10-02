import uuid

from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.sets import SetKind, Visibility
from app.main import app
from app.models.sets import QuestionSet
from app.storage import feedback, preparations

QUESTION_ID = uuid.uuid4()


def sign_in(uid="owner"):
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=f"{uid}@example.com", email_verified=True, name="Ann"
    )


def question_set():
    return QuestionSet(
        id=uuid.uuid4(), kind=SetKind.PREPARATION, owner_id="owner", visibility=Visibility.PRIVATE
    )


def test_owner_can_rate_and_read_question(client, monkeypatch):
    stored = {}

    async def fake_get(question_id):
        return question_set()

    async def fake_rate(question_id, user_id, value):
        stored["value"] = value

    async def fake_mine(question_id, user_id):
        return stored.get("value")

    monkeypatch.setattr(preparations, "get_for_question", fake_get)
    monkeypatch.setattr(feedback, "rate_question", fake_rate)
    monkeypatch.setattr(feedback, "my_question_rating", fake_mine)
    sign_in()

    empty = client.get(f"/questions/{QUESTION_ID}/rating")
    put = client.put(f"/questions/{QUESTION_ID}/rating", json={"value": 1})
    again = client.put(f"/questions/{QUESTION_ID}/rating", json={"value": -1})
    saved = client.get(f"/questions/{QUESTION_ID}/rating")

    assert empty.json() == {"value": None}
    assert put.status_code == 204
    assert again.status_code == 204
    assert saved.json() == {"value": -1}

    app.dependency_overrides.clear()
