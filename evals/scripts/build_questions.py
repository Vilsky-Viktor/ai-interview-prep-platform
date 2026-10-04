"""Builds datasets/questions.json: reference questions for every subtopic in datasets/inputs.json,
written by the generation service's own prompt and the model its settings give a learner's kit
of that level (KIT_MODEL, HARD_KIT_MODEL).

Run in the generation container: evals/run.sh generation build_questions.py [--per-subtopic 5]
Costs about $0.02 per subtopic on gpt-6.1-sol (48 subtopics: about $1).

To test another model or effort on the same subtopics, without touching the frozen dataset:
    MODEL=gpt-6-luna EFFORT=high evals/run.sh generation build_questions.py --label luna-high
writes results/questions_<label>.json, which review_questions.py and check_code.py read."""

import argparse
import asyncio
import time
from datetime import UTC, datetime

from common import DATASETS, RESULTS, cost, generation_models, load, save
from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.messages import HumanMessage

from app.config.settings import settings
from app.constants.generation import DISTRACTORS, MAX_OPTION_CHARS
from app.constants.kinds import GenerationKind
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
    structured = llm.get_generation_llm(
        GenerationKind.PREPARATION, domain["level"]
    ).with_structured_output(QuestionItemList)
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


async def main(per_subtopic: int, label: str | None) -> None:
    models = generation_models(settings)
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

    started = time.monotonic()

    with get_usage_metadata_callback() as usage:
        batches = await asyncio.gather(*(one(call) for call in calls))

    items = [item for batch in batches for item in batch]

    for index, item in enumerate(items):
        item["id"] = f"q{index:04d}"

    seconds = round(time.monotonic() - started)
    spent = sum(cost(name, metadata) for name, metadata in usage.usage_metadata.items())
    save(
        RESULTS / f"questions_{label}.json" if label else DATASETS / "questions.json",
        {
            "about": "Reference questions, frozen: build_questions.py writes them with the "
            "generation prompt of the date below. Reviewed in reviews.json; altered in "
            "key_traps.json.",
            "model": models,
            "built": datetime.now(UTC).date().isoformat(),
            "items": items,
        },
    )
    print(f"{models}: {len(items)} questions from {len(calls)} subtopics, ${spent:.2f}, {seconds}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-subtopic", type=int, default=5)
    parser.add_argument("--label", help="write results/questions_<label>.json instead")
    args = parser.parse_args()
    asyncio.run(main(args.per_subtopic, args.label))
