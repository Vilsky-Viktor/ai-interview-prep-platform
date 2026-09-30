import asyncio
import uuid

from app.auth import current_user
from app.integrations import library, llm
from app.main import app
from app.schemas.questions import AnswerItem, AnswerList, NewQuestion
from app.schemas.regenerate import QuestionContext
from app.schemas.user import User
from app.services.regenerate import regenerate

QUESTION_ID = uuid.uuid4()


def context():
    return QuestionContext(
        set_id=uuid.uuid4(),
        kind="preparation",
        owner_id="ann",
        level="medium",
        topic="Python",
        subtopics=["Asyncio"],
        existing=["What is the GIL?", "When is asyncio a good fit?"],
    )


class FakeStructured:
    def __init__(self, schema, questions):
        self.schema = schema
        self.questions = questions

    async def ainvoke(self, messages):
        if self.schema is NewQuestion:
            return NewQuestion(question=self.questions.pop(0))

        return AnswerList(
            answers=[
                AnswerItem(id=0, answer="Answer", correct_option="Right", distractors=["A", "B", "C"])
            ]
        )


class FakeLLM:
    def __init__(self, questions):
        self.questions = questions

    def with_structured_output(self, schema):
        return FakeStructured(schema, self.questions)


def test_skips_duplicates_and_saves_new_question(monkeypatch):
    fake = FakeLLM(["  what is the  GIL? ", "How do you cancel an asyncio task?"])
    saved = {}

    async def fake_replace(question_id, question):
        saved["id"] = question_id
        saved["question"] = question

    monkeypatch.setattr(llm, "get_question_llm", lambda: fake)
    monkeypatch.setattr(llm, "get_llm", lambda: fake)
    monkeypatch.setattr(library, "replace_question", fake_replace)

    result = asyncio.run(regenerate(QUESTION_ID, context()))

    assert result.text == "How do you cancel an asyncio task?"
    assert saved["id"] == QUESTION_ID
    assert saved["question"].reference_answer == "Answer"
    assert sum(option.correct for option in saved["question"].options) == 1


def test_gives_up_when_every_attempt_duplicates(monkeypatch):
    fake = FakeLLM(["What is the GIL?"] * 3)

    async def fake_replace(question_id, question):
        raise AssertionError("must not save a duplicate")

    monkeypatch.setattr(llm, "get_question_llm", lambda: fake)
    monkeypatch.setattr(library, "replace_question", fake_replace)

    assert asyncio.run(regenerate(QUESTION_ID, context())) is None


def test_only_owner_can_regenerate(client, monkeypatch):
    async def fake_context(_question_id):
        return context()

    monkeypatch.setattr(library, "get_question_context", fake_context)
    app.dependency_overrides[current_user] = lambda: User(
        uid="bob", email="bob@example.com", email_verified=True, name="Bob"
    )
    response = client.post(f"/questions/{QUESTION_ID}/regenerate")
    app.dependency_overrides.clear()

    assert response.status_code == 404
