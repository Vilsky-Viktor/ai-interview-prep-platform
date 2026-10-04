"""Builds datasets/questions.json: reference questions for every subtopic in datasets/inputs.json,
written by the generation service's own prompt and model (GENERATION_MODEL, LLM_REASONING_EFFORT).

Run in the generation container: evals/run.sh generation build_questions.py [--per-subtopic 5]
Costs about $0.02 per subtopic on gpt-6.1-sol (48 subtopics: about $1)."""

import argparse
import asyncio
from datetime import UTC, datetime

from common import DATASETS, cost, load, save
from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.messages import HumanMessage

from app.config.settings import settings
from app.constants.generation import DISTRACTORS, MAX_OPTION_CHARS
from app.helpers.questions import build_options, with_example
from app.integrations import llm
from app.prompts.questions import QUESTIONS_PROMPT
from app.schemas.questions import QuestionItemList
from app.services.nodes.questions import focus_for


async def subtopic_questions(domain: dict, topic: str, subtopic: str, count: int) -> list[dict]:
    prompt = QUESTIONS_PROMPT.format(
        level=domain["level"],
        topic=topic,
        subtopic=subtopic,
        focus=focus_for(0, 1),
        count=count,
        distractors=DISTRACTORS,
        max_chars=MAX_OPTION_CHARS,
        existing="None",
        language="English",
    )
    structured = llm.get_llm().with_structured_output(QuestionItemList)
    result = await structured.ainvoke([HumanMessage(content=prompt)])
    items = []

    for item in result.items:
        options = None if item.ambiguous else build_options(item.correct_option, item.distractors)

        if options:
            items.append(
                {
                    "domain": domain["id"],
                    "level": domain["level"],
                    "topic": topic,
                    "subtopic": subtopic,
                    "question": with_example(item.question, item.example),
                    "options": options,
                }
            )

    return items[:count]


async def main(per_subtopic: int) -> None:
    domains = load(DATASETS / "inputs.json")["domains"]
    calls = [
        (domain, topic["topic"], subtopic)
        for domain in domains
        for topic in domain["topics"]
        for subtopic in topic["subtopics"]
    ]
    limit = asyncio.Semaphore(8)

    async def one(call):
        async with limit:
            return await subtopic_questions(*call, per_subtopic)

    with get_usage_metadata_callback() as usage:
        batches = await asyncio.gather(*(one(call) for call in calls))

    items = [item for batch in batches for item in batch]

    for index, item in enumerate(items):
        item["id"] = f"q{index:04d}"

    spent = sum(cost(name, metadata) for name, metadata in usage.usage_metadata.items())
    save(
        DATASETS / "questions.json",
        {
            "about": "Reference questions, frozen: build_questions.py writes them with the "
            "generation prompt of the date below. Reviewed in reviews.json; altered in "
            "key_traps.json.",
            "model": f"{settings.generation_model} ({settings.llm_reasoning_effort})",
            "built": datetime.now(UTC).date().isoformat(),
            "items": items,
        },
    )
    print(f"{len(items)} questions from {len(calls)} subtopics, ${spent:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-subtopic", type=int, default=5)
    asyncio.run(main(parser.parse_args().per_subtopic))
