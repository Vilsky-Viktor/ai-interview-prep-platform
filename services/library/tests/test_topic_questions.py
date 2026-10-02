import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

from prepza_common.auth import current_user
from prepza_common.user import User

from app.constants.sets import Access, SetKind, Visibility
from app.main import app
from app.models.sets import QuestionSet
from app.storage import feedback, preparations

TOPIC_ID = uuid.uuid4()
QUESTION_ID = uuid.uuid4()


def test_topic_questions_are_text_only(client, monkeypatch):
    topic = SimpleNamespace(questions=[SimpleNamespace(id=QUESTION_ID, text="What is a lock?")])

    async def fake_found(_topic_id):
        return SimpleNamespace(), topic

    async def fake_access(_question_set, _user_id):
        return Access.PUBLIC

    async def fake_stats(_question_ids):
        return {QUESTION_ID: {"likes": 2, "dislikes": 0, "reports": 1}}

    monkeypatch.setattr(preparations, "get_topic_with_question_texts", fake_found)
    monkeypatch.setattr("app.routers.preparations.access_for", fake_access)
    monkeypatch.setattr(feedback, "question_stats", fake_stats)

    response = client.get(f"/preparations/topics/{TOPIC_ID}/questions")

    assert response.status_code == 200
    assert response.json() == [
        {"id": str(QUESTION_ID), "text": "What is a lock?", "likes": 2, "dislikes": 0, "reports": 1}
    ]


def test_only_owner_reads_reports(client, monkeypatch):
    question_set = QuestionSet(
        id=uuid.uuid4(), kind=SetKind.PREPARATION, owner_id="owner", visibility=Visibility.PUBLIC
    )
    report = SimpleNamespace(
        id=uuid.uuid4(), reason="unclear", comment="Too vague", created_at=datetime.now(UTC)
    )

    async def fake_set(_question_id):
        return question_set

    async def fake_reports(_question_id, offset=0, limit=None):
        return [report]

    monkeypatch.setattr(preparations, "get_for_question", fake_set)
    monkeypatch.setattr(feedback, "list_reports", fake_reports)
    url = f"/questions/{QUESTION_ID}/reports"

    for uid, expected in (("stranger", 404), ("owner", 200)):
        app.dependency_overrides[current_user] = lambda uid=uid: User(
            uid=uid, email=f"{uid}@example.com", email_verified=True, name="Ann"
        )
        response = client.get(url)

        assert response.status_code == expected

    assert response.json()[0]["comment"] == "Too vague"
    assert "user_id" not in response.json()[0]

    app.dependency_overrides.clear()


def test_hidden_topic_questions_are_not_found(client, monkeypatch):
    async def fake_found(_topic_id):
        return None

    monkeypatch.setattr(preparations, "get_topic_with_question_texts", fake_found)

    response = client.get(f"/preparations/topics/{TOPIC_ID}/questions")

    assert response.status_code == 404
