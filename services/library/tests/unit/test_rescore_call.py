import uuid

from app.integrations import rounds
from app.services import outbox
from app.storage import preparations
from tests.unit.test_internal import token

QUESTION_ID = uuid.uuid4()
OPTIONS = [{"answer": "Debit cash", "correct": False}, {"answer": "Credit cash", "correct": True}]


def test_replacing_a_question_has_its_answers_marked_again(client, monkeypatch):
    calls = []

    async def fake_replace(question_id, text, options):
        calls.append(("replace", text))

    async def fake_flush():
        return None

    async def fake_rescore(question_id, text, options):
        calls.append(("rescore", text, options))
        # Rounds being down doesn't undo the fix.
        raise RuntimeError("rounds is down")

    monkeypatch.setattr(preparations, "replace_question", fake_replace)
    monkeypatch.setattr(outbox, "flush_quietly", fake_flush)
    monkeypatch.setattr(rounds, "rescore_question", fake_rescore)

    response = client.put(
        f"/internal/questions/{QUESTION_ID}",
        json={"text": "What is debit?", "options": OPTIONS},
        headers={"Authorization": f"Bearer {token()}"},
    )

    assert response.status_code == 204
    assert calls == [("replace", "What is debit?"), ("rescore", "What is debit?", OPTIONS)]
