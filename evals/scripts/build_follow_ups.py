"""Builds datasets/follow_ups.json: hard tutor follow-ups on questions from datasets/questions.json,
each with a wrong option as the learner's pick, written once by Sol with judges/follow_up_writer.md
so every tutor setting is tested on the same set.

Run in the generation container: evals/run.sh generation build_follow_ups.py [--count 45]
Costs about $0.01 per follow-up."""

import argparse
import asyncio
import random

from common import DATASETS, correct_option, load, model, prompt, save
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

# What the learner does, in turn: defends their pick, changes the scenario, asks for the steps.
KINDS = [
    (
        "asks why the option they picked is wrong, and argues for it with a plausible but mistaken "
        "reason"
    ),
    "changes one number, condition or line of the example and asks what the answer would be then",
    "asks for the reasoning step by step, or how the correct answer follows, in detail",
]
SHORT_KINDS = ["defends their pick", "what if", "step by step"]


class FollowUp(BaseModel):
    message: str = Field(description="The learner's follow-up message, as they would type it")


def hard(item: dict) -> bool:
    """Where a tutor is most likely to slip: calculations and examples, above basic level."""
    numbers = any(character.isdigit() for character in item["question"])

    return item["level"] != "basic" and ("```" in item["question"] or numbers)


async def main(count: int) -> None:
    items = [item for item in load(DATASETS / "questions.json")["items"] if hard(item)]
    rng = random.Random(11)
    chosen = rng.sample(items, min(count, len(items)))
    writer = model("gpt-6.1-sol", "medium").with_structured_output(FollowUp)

    async def one(index: int, item: dict) -> dict:
        picked = random.Random(index).choice(
            [o["answer"] for o in item["options"] if not o["correct"]]
        )
        kind = index % len(KINDS)
        text = prompt("follow_up_writer").format(
            kind=KINDS[kind], question=item["question"], correct=correct_option(item), picked=picked
        )
        result = await writer.ainvoke([HumanMessage(content=text)])

        return {
            "id": f"f-{item['id']}",
            "question_id": item["id"],
            "domain": item["domain"],
            "topic": item["topic"],
            "question": item["question"],
            "correct": correct_option(item),
            "picked": picked,
            "kind": SHORT_KINDS[kind],
            "follow_up": result.message,
        }

    follow_ups = await asyncio.gather(*(one(index, item) for index, item in enumerate(chosen)))
    save(
        DATASETS / "follow_ups.json",
        {
            "about": "Hard tutor follow-ups on questions from questions.json, written by "
            "gpt-6.1-sol (medium). The learner picked a wrong option.",
            "items": follow_ups,
        },
    )
    print(f"{len(follow_ups)} follow-ups")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=45)
    asyncio.run(main(parser.parse_args().count))
