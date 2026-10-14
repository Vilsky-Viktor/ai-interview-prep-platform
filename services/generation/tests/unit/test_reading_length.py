import asyncio
import logging
import uuid
from types import SimpleNamespace

from app.constants.generation import MAX_EXAMPLE_LINES, MAX_OPTION_CHARS, MAX_QUESTION_CHARS
from app.helpers.questions import readable
from app.integrations import library, llm
from app.prompts.questions import QUESTIONS_PROMPT
from app.prompts.regenerate import REGENERATE_PROMPT
from app.schemas.questions import QuestionItem, QuestionItemList
from app.services.nodes.questions import generate_questions
from app.services.pipeline import log_cost
from app.services.regenerate import regenerate
from tests.unit.test_regenerate import QUESTION_ID, FakeEmbeddings, context
from tests.unit.test_regenerate import FakeLLM as RegenerateLLM
from tests.unit.test_runaway_output import FakeLLM, question_task

LONG = "word " * (MAX_QUESTION_CHARS // 5 + 1)


def test_a_question_reads_within_a_minute():
    assert readable("x" * MAX_QUESTION_CHARS, "\n".join(["line"] * MAX_EXAMPLE_LINES))
    assert not readable("x" * (MAX_QUESTION_CHARS + 1), None)
    assert not readable("What does this print?", "\n".join(["line"] * (MAX_EXAMPLE_LINES + 1)))
    # A fence the model added isn't a line of the example.
    assert readable(
        "What does this print?", "```\n" + "\n".join(["l"] * MAX_EXAMPLE_LINES) + "\n```"
    )


def test_every_question_prompt_sets_the_reading_budget():
    for prompt in (QUESTIONS_PROMPT, REGENERATE_PROMPT):
        assert "within one minute" in prompt
        assert "isn't their own" in prompt
        assert "at most 40 words" in prompt


def item(question, example=None, correct="Right"):
    return QuestionItem(
        question=question,
        example=example,
        correct_option=correct,
        distractors=["A", "B", "C"],
        ambiguous=False,
    )


def test_questions_too_long_to_read_in_a_minute_are_dropped(monkeypatch):
    fake = FakeLLM(
        [
            QuestionItemList(
                items=[
                    item(LONG),
                    item("What does this print?", "\n".join(["print(1)"] * 20)),
                    item("Which account is debited?", correct="x" * (MAX_OPTION_CHARS + 1)),
                    item("Which account is credited?"),
                ]
            )
        ]
    )
    monkeypatch.setattr(llm, "get_generation_llm", lambda *_: fake)

    result = asyncio.run(generate_questions(question_task(count=4)))

    [entry] = result["question_pool"]
    assert [question["text"] for question in entry["questions"]] == ["Which account is credited?"]


def test_a_rewritten_question_too_long_to_read_is_written_again(monkeypatch):
    fake = RegenerateLLM([LONG, "How do you cancel an asyncio task?"])

    async def replace(question_id, question):
        pass

    monkeypatch.setattr(llm, "get_generation_llm", lambda *_: fake)
    monkeypatch.setattr(library, "replace_question", replace)
    monkeypatch.setattr(llm, "get_embeddings", FakeEmbeddings)

    result = asyncio.run(regenerate(QUESTION_ID, context()))

    assert result.text == "How do you cancel an asyncio task?"


def test_each_run_logs_what_it_spent(caplog):
    generation = SimpleNamespace(id=uuid.uuid4(), kind="template")
    usage = {"gpt-6.1-sol": {"input_tokens": 500_000, "output_tokens": 100_000}}

    with caplog.at_level(logging.INFO):
        log_cost(generation, usage)

    assert f"Generation {generation.id} (template) spent $2.00" in caplog.text
