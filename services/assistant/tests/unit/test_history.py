import uuid

from langchain_core.messages import AIMessage, HumanMessage

from app.helpers.history import history
from app.models.conversations import Message


def message(role, content):
    return Message(id=uuid.uuid4(), role=role, content=content)


def test_a_later_turn_reads_only_the_stored_text():
    rows = [message("user", "Who passed?"), message("assistant", "Ann passed.")]

    assert history(rows, 1_000) == [
        HumanMessage(content="Who passed?"),
        AIMessage(content="Ann passed."),
    ]


def test_only_the_latest_messages_that_fit_are_kept():
    rows = [message("user", "x" * 50), message("assistant", "y" * 30), message("user", "z" * 30)]

    assert history(rows, 70) == [AIMessage(content="y" * 30), HumanMessage(content="z" * 30)]


def test_a_failed_answer_without_text_adds_nothing():
    assert history([message("assistant", "")], 1_000) == []
