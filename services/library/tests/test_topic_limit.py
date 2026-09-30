import uuid
from types import SimpleNamespace

from app.auth import current_user
from app.constants.sets import SetKind, Visibility
from app.main import app
from app.models.sets import QuestionSet
from app.schemas.user import User
from app.storage import preparations

TOPIC_ID = uuid.uuid4()
URL = f"/preparations/topics/{TOPIC_ID}/limit"


def setup(monkeypatch, uid, saved):
    question_set = QuestionSet(
        id=uuid.uuid4(), kind=SetKind.PREPARATION, owner_id="owner", visibility=Visibility.PUBLIC
    )
    topic = SimpleNamespace(questions=[SimpleNamespace(id=uuid.uuid4()) for _ in range(10)])

    async def fake_found(_topic_id):
        return question_set, topic

    async def fake_save(topic_id, limit):
        saved.append(limit)

    monkeypatch.setattr(preparations, "get_topic_with_questions", fake_found)
    monkeypatch.setattr(preparations, "set_topic_limit", fake_save)
    app.dependency_overrides[current_user] = lambda: User(
        uid=uid, email=f"{uid}@example.com", email_verified=True, name="Ann"
    )


def test_owner_sets_limit_within_topic_size(client, monkeypatch):
    saved = []
    setup(monkeypatch, "owner", saved)

    assert client.put(URL, json={"limit": 11}).status_code == 422
    assert client.put(URL, json={"limit": 0}).status_code == 422
    assert client.put(URL, json={"limit": 5}).status_code == 204
    assert client.put(URL, json={"limit": None}).status_code == 204
    assert saved == [5, None]

    app.dependency_overrides.clear()


def test_only_owner_sets_limit(client, monkeypatch):
    saved = []
    setup(monkeypatch, "stranger", saved)

    assert client.put(URL, json={"limit": 5}).status_code == 404
    assert saved == []

    app.dependency_overrides.clear()
