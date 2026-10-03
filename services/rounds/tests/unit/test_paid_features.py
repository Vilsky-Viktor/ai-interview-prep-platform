import asyncio
import uuid

import pytest
from fastapi import HTTPException
from firebase_admin import auth as firebase_auth
from prepza_common.user import User

from app.integrations import billing
from app.models.chat import ChatMessage
from app.schemas.library import TopicQuestions
from app.services import certificate_purchase
from app.services.public_kits import check_daily_limit
from app.storage import certificates, progress, rounds
from app.storage import chat as chat_storage
from tests.unit.test_review_chat import make_round

ANN = User(uid="ann", email="ann@example.com", email_verified=True, name="Ann")


def topic(author=None):
    return TopicQuestions.model_validate(
        {
            "id": str(uuid.uuid4()),
            "preparation_id": str(uuid.uuid4()),
            "title": "Ledgers",
            "questions": [],
            "public_author_id": author,
        }
    )


def started(monkeypatch, already=False, today=0):
    async def has_started(user_id, topic_id):
        return already

    async def count(user_id, since):
        return today

    monkeypatch.setattr(rounds, "has_started", has_started)
    monkeypatch.setattr(rounds, "public_topics_started_since", count)


def test_a_fourth_new_public_topic_a_day_is_refused(monkeypatch):
    started(monkeypatch, today=3)

    with pytest.raises(HTTPException) as refused:
        asyncio.run(check_daily_limit("ann", topic(author="bob")))

    assert refused.value.status_code == 429


@pytest.mark.parametrize(
    ("author", "already", "today"),
    [
        ("bob", False, 2),  # still within the day's three
        ("bob", True, 3),  # continuing a topic already started
        (None, False, 9),  # own or shared kits aren't limited
    ],
)
def test_the_daily_limit_lets_these_through(monkeypatch, author, already, today):
    started(monkeypatch, already, today)

    asyncio.run(check_daily_limit("ann", topic(author)))


def chat_setup(monkeypatch, turns_so_far, available=0):
    round_ = make_round()
    charged = []
    history = [
        message
        for _ in range(turns_so_far)
        for message in (
            ChatMessage(role="user", content="Why?"),
            ChatMessage(role="assistant", content="Because."),
        )
    ]

    async def fake_owned_answer(answer_id, user):
        return round_.answers[0], round_

    async def fake_list(answer_id):
        return history

    async def fake_add(answer_id, message, reply):
        pass

    async def fake_stream(messages):
        yield "Ok"

    async def fake_available(user_id):
        return available

    async def fake_charge(user_id, key):
        charged.append(key)

    monkeypatch.setattr(firebase_auth, "verify_id_token", lambda token: {"uid": "u1"})
    monkeypatch.setattr("app.routers.chat.get_owned_answer", fake_owned_answer)
    monkeypatch.setattr("app.routers.chat.stream_reply", fake_stream)
    monkeypatch.setattr(chat_storage, "list_messages", fake_list)
    monkeypatch.setattr(chat_storage, "add_exchange", fake_add)
    monkeypatch.setattr(billing, "available_credits", fake_available)
    monkeypatch.setattr(billing, "charge_chat_turn", fake_charge)

    return round_.answers[0].id, charged


def send(client, answer_id):
    return client.post(
        f"/answers/{answer_id}/chat",
        json={"message": "More?"},
        headers={"Authorization": "Bearer token"},
    )


def test_the_first_three_turns_on_a_question_are_free(client, monkeypatch):
    answer_id, charged = chat_setup(monkeypatch, turns_so_far=2)

    assert send(client, answer_id).status_code == 200
    assert charged == []


def test_the_fourth_turn_costs_a_credit_once_the_reply_arrived(client, monkeypatch):
    answer_id, charged = chat_setup(monkeypatch, turns_so_far=3, available=5)

    assert send(client, answer_id).status_code == 200
    assert charged == [f"{answer_id}:4"]


def test_a_paid_turn_without_credits_is_refused_before_the_reply(client, monkeypatch):
    answer_id, charged = chat_setup(monkeypatch, turns_so_far=3, available=0)

    response = send(client, answer_id)

    assert response.status_code == 402
    assert charged == []


def test_an_earned_certificate_on_a_public_kit_is_charged_then_issued(monkeypatch):
    bought = topic(author="bob")
    calls = []

    async def fake_topic(topic_id, user_id):
        return bought

    async def no_certificate(user_id, topic_id):
        return False

    async def fake_progress(user_id, topic_id):
        return []

    async def latest(user_id, topic_id):
        return make_round()

    async def charge(user_id, key, title, author_id):
        calls.append(("charge", key, title, author_id))

    async def create(certificate):
        calls.append(("issue", certificate.topic_title))

        return certificate

    monkeypatch.setattr(certificate_purchase.library, "get_topic_questions", fake_topic)
    monkeypatch.setattr(certificates, "has_for_topic", no_certificate)
    monkeypatch.setattr(progress, "for_topic", fake_progress)
    monkeypatch.setattr(rounds, "latest_finished", latest)
    monkeypatch.setattr(certificate_purchase, "coverage_score", lambda scores, texts: 90)
    monkeypatch.setattr(billing, "charge_certificate", charge)
    monkeypatch.setattr(certificates, "create", create)

    asyncio.run(certificate_purchase.buy_certificate(bought.id, ANN))

    assert calls == [("charge", f"ann:{bought.id}", "Ledgers", "bob"), ("issue", "Ledgers")]
