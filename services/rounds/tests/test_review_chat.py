import uuid

from firebase_admin import auth as firebase_auth
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.helpers.review import build_review
from app.helpers.scores import earns_certificate
from app.models.chat import ChatMessage
from app.models.rounds import Answer, Round
from app.services.chat import build_messages
from app.storage import chat as chat_storage

Q1, Q2 = uuid.uuid4(), uuid.uuid4()
OPTIONS = [{"answer": "Right", "correct": True}, {"answer": "Wrong", "correct": False}]


def make_round() -> Round:
    questions = [
        {"id": str(q), "text": f"Question {n}", "reference_answer": f"Ref {n}", "options": OPTIONS}
        for n, q in enumerate((Q1, Q2), start=1)
    ]
    answer = Answer(
        id=uuid.uuid4(), question_id=Q1, text="Mine", score=60, feedback="Missed X."
    )

    return Round(id=uuid.uuid4(), mode="open", questions=questions, answers=[answer])


def test_certificate_rules():
    assert earns_certificate("open", 10, 10, 70)
    assert not earns_certificate("open", 10, 10, 69)
    assert not earns_certificate("open", 9, 10, 99)
    assert not earns_certificate("choice", 10, 10, 100)
    assert not earns_certificate("open", 5, 5, None)


def test_review_hides_unanswered_reference_answers():
    first, second = build_review(make_round())

    assert first.reference_answer == "Ref 1"
    assert first.correct_option_index == 0
    assert first.answer.score == 60
    assert second.reference_answer is None
    assert second.correct_option_index is None
    assert second.answer is None


def test_chat_messages_include_context_and_history():
    round_ = make_round()
    history = [
        ChatMessage(role="user", content="Why?"),
        ChatMessage(role="assistant", content="Because."),
    ]

    messages = build_messages(round_, round_.answers[0], history, "And then?")

    assert isinstance(messages[0], SystemMessage)
    assert "Ref 1" in messages[0].content
    assert "Mine" in messages[0].content
    assert "Grade: 60/100" in messages[0].content
    assert [type(m) for m in messages[1:]] == [HumanMessage, AIMessage, HumanMessage]


def test_chat_streams_and_stores_exchange(client, monkeypatch):
    round_ = make_round()
    stored = []

    async def fake_owned_answer(answer_id, user):
        return round_.answers[0], round_

    async def fake_list(answer_id):
        return []

    async def fake_add(answer_id, message, reply):
        stored.append((message, reply))

    async def fake_stream(messages):
        for delta in ("Hel", "lo"):
            yield delta

    monkeypatch.setattr(firebase_auth, "verify_id_token", lambda token: {"uid": "u1"})
    monkeypatch.setattr("app.routers.chat.get_owned_answer", fake_owned_answer)
    monkeypatch.setattr("app.routers.chat.stream_reply", fake_stream)
    monkeypatch.setattr(chat_storage, "list_messages", fake_list)
    monkeypatch.setattr(chat_storage, "add_exchange", fake_add)

    response = client.post(
        f"/answers/{round_.answers[0].id}/chat",
        json={"message": " Explain "},
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    assert response.text == (
        'data: {"delta": "Hel"}\n\ndata: {"delta": "lo"}\n\ndata: {"done": true}\n\n'
    )
    assert stored == [("Explain", "Hello")]
