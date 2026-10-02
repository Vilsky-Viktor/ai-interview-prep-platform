import httpx

from app.integrations import generation
from app.main import app
from app.storage import preparations
from tests.test_question_rating import QUESTION_ID, question_set, sign_in


def call(client, monkeypatch, uid, reply):
    sent = []

    async def fake_get(question_id):
        return question_set()

    async def fake_regenerate(question_id, set_id, user_id):
        sent.append(user_id)

        return reply

    monkeypatch.setattr(preparations, "get_for_question", fake_get)
    monkeypatch.setattr(generation, "regenerate_question", fake_regenerate)
    sign_in(uid)
    response = client.post(f"/questions/{QUESTION_ID}/regenerate")
    app.dependency_overrides.clear()

    return response, sent


def reply(status, body):
    return httpx.Response(status, json=body, request=httpx.Request("POST", "http://generation"))


def test_owner_gets_the_new_question(client, monkeypatch):
    new = {"id": str(QUESTION_ID), "text": "A new question?"}
    response, sent = call(client, monkeypatch, "owner", reply(200, new))

    assert response.status_code == 200
    assert response.json() == new
    assert sent == ["owner"]


def test_someone_else_cannot_regenerate(client, monkeypatch):
    response, sent = call(client, monkeypatch, "bob", reply(200, {}))

    assert response.status_code == 404
    assert sent == []


def test_rate_limit_is_passed_through(client, monkeypatch):
    response, _ = call(client, monkeypatch, "owner", reply(429, {"detail": "Too many requests"}))

    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}
