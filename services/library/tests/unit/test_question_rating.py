import uuid

from app.storage import feedback
from tests.unit.test_internal import token

QUESTION_ID = uuid.uuid4()
AUTH = {"Authorization": f"Bearer {token()}"}


def test_a_candidate_rates_a_question_and_reads_it_back(client, monkeypatch):
    stored = {}
    reviewed = []

    async def fake_rate(question_id, user_id, value):
        stored[user_id] = value

    async def fake_mine(question_id, user_id):
        return stored.get(user_id)

    async def fake_review(question_id):
        reviewed.append(question_id)

    monkeypatch.setattr(feedback, "rate_question", fake_rate)
    monkeypatch.setattr(feedback, "my_question_rating", fake_mine)
    monkeypatch.setattr("app.routers.internal_feedback.review", fake_review)
    url = f"/internal/questions/{QUESTION_ID}/rating"

    empty = client.get(url, params={"user_id": "ann"}, headers=AUTH)
    put = client.put(url, json={"user_id": "ann", "value": 1}, headers=AUTH)
    again = client.put(url, json={"user_id": "ann", "value": -1}, headers=AUTH)
    saved = client.get(url, params={"user_id": "ann"}, headers=AUTH)

    assert empty.json() == {"value": None}
    assert (put.status_code, again.status_code) == (204, 204)
    assert saved.json() == {"value": -1}
    # Every vote goes to the quality review, which may flag the question.
    assert reviewed == [QUESTION_ID, QUESTION_ID]
