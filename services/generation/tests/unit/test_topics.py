import asyncio

from app.constants.generation import MAX_TOPICS
from app.integrations import llm
from app.schemas.topics import TopicList, TopicStructure
from app.services.nodes.topics import revise_topics


def topic_list(count: int) -> TopicList:
    return TopicList(
        topics=[TopicStructure(main_topic=f"Topic {i}", subtopics=["A"]) for i in range(count)]
    )


class FakeStructured:
    def __init__(self, calls):
        self.calls = calls

    async def ainvoke(self, messages):
        self.calls.append(messages)

        if "but the limit is" in messages[-1].content:
            return topic_list(MAX_TOPICS)

        return topic_list(MAX_TOPICS + 1)


class FakeLLM:
    def __init__(self, calls):
        self.calls = calls

    def with_structured_output(self, schema):
        return FakeStructured(self.calls)


def test_revision_over_the_limit_is_sent_back_to_merge(monkeypatch):
    calls = []
    monkeypatch.setattr(llm, "get_generation_llm", lambda *_: FakeLLM(calls))
    state = {
        "level": "medium",
        "requirements": ["Python"],
        "topics": [{"main_topic": f"Topic {i}", "subtopics": ["A"]} for i in range(MAX_TOPICS)],
        "feedback": "Add Flask basics",
    }

    result = asyncio.run(revise_topics(state))

    assert len(result["topics"]) == MAX_TOPICS
    assert len(calls) == 2
    assert f"You returned {MAX_TOPICS + 1} main topics" in calls[1][-1].content
