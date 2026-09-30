import asyncio
import re

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.config.settings import settings
from app.integrations import llm
from app.schemas.extraction import JobExtraction
from app.schemas.questions import AnswerItem, AnswerList, QuestionList
from app.schemas.topics import TopicList, TopicStructure
from app.services.graph import build_graph


class FakeStructured:
    def __init__(self, schema):
        self.schema = schema

    async def ainvoke(self, messages):
        prompt = messages[-1].content

        if self.schema is JobExtraction:
            return JobExtraction(
                title="Backend", company_name="", requirements=["Python"], level="medium"
            )

        if self.schema is TopicList:
            return TopicList(
                topics=[
                    TopicStructure(main_topic="Python", subtopics=["Asyncio", "Typing"]),
                    TopicStructure(main_topic="SQL", subtopics=["Joins"]),
                ]
            )

        if self.schema is QuestionList:
            subtopic = re.search(r"Subtopic: (.+)", prompt).group(1)

            return QuestionList(questions=[f"{subtopic} question {i}" for i in range(70)])

        ids = [int(match) for match in re.findall(r"^\[(\d+)\]", prompt, re.MULTILINE)]

        return AnswerList(
            answers=[
                AnswerItem(
                    id=i, answer="Answer", correct_option="Right", distractors=["W1", "W2", "W3"]
                )
                for i in ids
            ]
        )


class FakeLLM:
    def with_structured_output(self, schema):
        return FakeStructured(schema)


async def run_graph():
    graph = build_graph(InMemorySaver())
    config = {"configurable": {"thread_id": "test"}}
    interrupts = []

    async for chunk in graph.astream({"input_text": "Job"}, config, stream_mode="updates"):
        interrupts.extend(chunk.get("__interrupt__", ()))

    assert len(interrupts[0].value["topics"]) == 2

    resume = Command(resume={"selected": [0], "instructions": ""})

    async for _ in graph.astream(resume, config, stream_mode="updates"):
        pass

    return (await graph.aget_state(config)).values


@pytest.mark.parametrize("per_topic", [100, 12])
def test_full_graph(monkeypatch, per_topic):
    monkeypatch.setattr(llm, "get_llm", FakeLLM)
    monkeypatch.setattr(llm, "get_question_llm", FakeLLM)
    monkeypatch.setattr(settings, "questions_per_topic", per_topic)

    values = asyncio.run(run_graph())
    [topic] = values["final"]

    assert topic["topic"] == "Python"
    assert len(topic["questions"]) == per_topic
    assert all(topic["answers"])
    assert all(len(options) == 4 for options in topic["answer_options"])
