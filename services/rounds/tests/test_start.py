import uuid
from datetime import UTC, datetime

import pytest

from app.auth import current_user
from app.helpers.rounds import round_questions
from app.integrations import library
from app.main import app
from app.models.rounds import Round
from app.schemas.library import Question, TopicQuestions
from app.schemas.user import User
from app.storage import progress, rounds

TOPIC_ID = uuid.uuid4()
ROUND_ID = uuid.uuid4()


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def sign_in():
    app.dependency_overrides[current_user] = lambda: User(
        uid="member", email="member@example.com", email_verified=True, name="Ann"
    )


def topic():
    return TopicQuestions(
        id=TOPIC_ID,
        preparation_id=uuid.uuid4(),
        title="Python",
        questions=[
            Question(id=uuid.uuid4(), text="Q", reference_answer="A", options=[]),
        ],
    )


def unfinished(mode="choice"):
    return Round(
        id=ROUND_ID,
        user_id="member",
        topic_id=TOPIC_ID,
        preparation_id=uuid.uuid4(),
        topic_title="Python",
        mode=mode,
        status="in_progress",
        questions=[{"id": str(uuid.uuid4()), "text": "Q", "reference_answer": "A", "options": []}],
        answers=[],
        certificate=None,
        started_at=datetime.now(UTC),
        finished_at=None,
        final_score=None,
    )


def post(client, mode="choice"):
    return client.post("/rounds", json={"topic_id": str(TOPIC_ID), "mode": mode})


def test_resumes_unfinished_round(client, monkeypatch):
    created = []

    async def fake_topic(topic_id, user_id):
        return topic()

    async def fake_in_progress(user_id, topic_id, mode):
        return unfinished(mode)

    async def fake_create(user_id, topic, mode, seen):
        created.append(mode)

    monkeypatch.setattr(library, "get_topic_questions", fake_topic)
    monkeypatch.setattr(rounds, "get_in_progress", fake_in_progress)
    monkeypatch.setattr(rounds, "create", fake_create)
    sign_in()

    response = post(client)

    assert response.status_code == 200
    assert response.json()["id"] == str(ROUND_ID)
    assert created == []


def test_creates_when_none_unfinished(client, monkeypatch):
    new_round = unfinished()
    new_round.id = uuid.uuid4()

    async def fake_topic(topic_id, user_id):
        return topic()

    async def fake_in_progress(user_id, topic_id, mode):
        return None

    async def fake_progress(user_id, topic_id, mode):
        return []

    async def fake_create(user_id, topic, mode, seen):
        return new_round

    monkeypatch.setattr(library, "get_topic_questions", fake_topic)
    monkeypatch.setattr(rounds, "get_in_progress", fake_in_progress)
    monkeypatch.setattr(progress, "for_topic", fake_progress)
    monkeypatch.setattr(rounds, "create", fake_create)
    sign_in()

    response = post(client)

    assert response.status_code == 201
    assert response.json()["id"] == str(new_round.id)


def test_limited_topic_takes_a_random_subset():
    limited = TopicQuestions(
        id=TOPIC_ID,
        preparation_id=uuid.uuid4(),
        title="Python",
        question_limit=5,
        questions=[
            Question(id=uuid.uuid4(), text=f"Q{index}", reference_answer="A", options=[])
            for index in range(100)
        ],
    )
    picked = round_questions(limited, {})

    assert len(picked) == 5
    assert len({question["id"] for question in picked}) == 5
    assert len(round_questions(topic(), {})) == 1


def test_unanswered_questions_come_first():
    questions = [
        Question(id=uuid.uuid4(), text=f"Q{index}", reference_answer="A", options=[])
        for index in range(10)
    ]
    limited = TopicQuestions(
        id=TOPIC_ID, preparation_id=uuid.uuid4(), title="Python", question_limit=3, questions=questions
    )
    latest = {str(question.id): 100 for question in questions[:7]}
    picked = {question["id"] for question in round_questions(limited, latest)}

    assert picked == {str(question.id) for question in questions[7:]}


def test_weakest_questions_come_next_once_all_answered():
    questions = [
        Question(id=uuid.uuid4(), text=f"Q{index}", reference_answer="A", options=[])
        for index in range(10)
    ]
    limited = TopicQuestions(
        id=TOPIC_ID, preparation_id=uuid.uuid4(), title="Python", question_limit=3, questions=questions
    )
    latest = {str(question.id): 90 for question in questions}
    weak = {str(questions[2].id): 10, str(questions[5].id): 40, str(questions[8].id): 30}
    picked = {question["id"] for question in round_questions(limited, {**latest, **weak})}

    assert picked == set(weak)


def test_owner_can_delete_round(client, monkeypatch):
    removed = []

    rebuilt = []
    answered = [uuid.uuid4()]

    async def fake_remove(round_id, user_id):
        removed.append((str(round_id), user_id))

        return answered

    async def fake_rebuild(user_id, question_ids):
        rebuilt.append((user_id, question_ids))

    monkeypatch.setattr(rounds, "remove", fake_remove)
    monkeypatch.setattr(progress, "rebuild", fake_rebuild)
    sign_in()

    assert client.delete(f"/rounds/{ROUND_ID}").status_code == 204
    assert removed == [(str(ROUND_ID), "member")]
    assert rebuilt == [("member", answered)]


def test_missing_round_delete_is_404(client, monkeypatch):
    async def fake_remove(round_id, user_id):
        return None

    monkeypatch.setattr(rounds, "remove", fake_remove)
    sign_in()

    assert client.delete(f"/rounds/{ROUND_ID}").status_code == 404
