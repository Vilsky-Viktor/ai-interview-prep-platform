import asyncio

from app.constants.generation import MAX_OPTION_CHARS
from app.integrations import llm
from app.schemas.questions import AnswerItem, AnswerList
from app.services.nodes.answers import generate_answers

TOO_LONG = "x" * (MAX_OPTION_CHARS + 1)


class FakeStructured:
    """First reply has a correct option over the limit; the retry has a short one."""

    def __init__(self):
        self.calls = 0

    async def ainvoke(self, messages):
        self.calls += 1
        correct = TOO_LONG if self.calls == 1 else "Short and right"

        return AnswerList(
            answers=[AnswerItem(id=0, correct_option=correct, distractors=["A", "B", "C"], ambiguous=False)]
        )


class FakeLLM:
    def __init__(self):
        self.structured = FakeStructured()

    def with_structured_output(self, schema):
        return self.structured


def test_correct_option_over_the_limit_is_retried(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr(llm, "get_llm", lambda: fake)

    result = asyncio.run(
        generate_answers(
            {
                "topic_index": 0,
                "topic": "Topic",
                "start": 0,
                "questions": ["Question?"],
                "level": "medium",
            }
        )
    )
    [options] = result["answer_pool"][0]["options"]

    assert fake.structured.calls == 2
    assert [option["answer"] for option in options if option["correct"]] == ["Short and right"]
    assert all(len(option["answer"]) <= MAX_OPTION_CHARS for option in options)


class AmbiguousStructured:
    def __init__(self):
        self.calls = 0

    async def ainvoke(self, messages):
        self.calls += 1

        return AnswerList(
            answers=[
                AnswerItem(id=0, correct_option="try", distractors=["catch", "finally", "except"], ambiguous=True),
                AnswerItem(id=1, correct_option="Right", distractors=["A", "B", "C"], ambiguous=False),
            ]
        )


def test_ambiguous_question_is_dropped_without_retry(monkeypatch):
    fake = FakeLLM()
    fake.structured = AmbiguousStructured()
    monkeypatch.setattr(llm, "get_llm", lambda: fake)

    result = asyncio.run(
        generate_answers(
            {
                "topic_index": 0,
                "topic": "Python",
                "start": 0,
                "questions": ["Which keyword is used to handle exceptions?", "Clear question?"],
                "level": "medium",
            }
        )
    )
    ambiguous, clear = result["answer_pool"][0]["options"]

    assert fake.structured.calls == 1
    assert ambiguous == []
    assert len(clear) == 4
