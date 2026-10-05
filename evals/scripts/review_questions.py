"""Measures a set of questions, and has the judge review them with judges/question_review.md.

    evals/run.sh generation review_questions.py datasets/questions.json [--sample 40]
    evals/run.sh generation review_questions.py datasets/key_traps.json        # catch rate
    evals/run.sh generation review_questions.py results/test_x.json --sample 40  # a new test
    evals/run.sh generation review_questions.py datasets/questions.json --save-reference
    JUDGE_MODEL=gpt-6-luna evals/run.sh generation review_questions.py datasets/questions.json \\
        --compare-reference                                                    # test a judge

Measurements cost nothing; a review costs about $0.01-0.02 per question with Sol at high
reasoning, the default judge (JUDGE_MODEL, JUDGE_EFFORT)."""

import argparse
import asyncio
import random
import statistics

from common import (
    DATASETS,
    EVALS,
    JUDGE_EFFORT,
    JUDGE_MODEL,
    RESULTS,
    correct_option,
    judge,
    load,
    options_text,
    prompt,
    question_items,
    save,
)
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field


class Review(BaseModel):
    key_correct: bool = Field(description="The option marked correct is actually correct")
    single_correct: bool = Field(description="Exactly one option can be defended as correct")
    distractors: int = Field(ge=1, le=5, description="How tempting the wrong options are")
    clarity: int = Field(ge=1, le=5, description="How clear and unambiguous the question is")
    relevance: int = Field(ge=1, le=5, description="How useful it is at this level")
    issue: str = Field(description="The main problem in a few words, or empty")


def measure(items: list[dict]) -> dict:
    """What can be counted without a judge."""
    longest = 0

    for item in items:
        sizes = [len(option["answer"]) for option in item["options"]]
        correct = len(correct_option(item))
        longest += correct == max(sizes) and sizes.count(correct) == 1

    return {
        "questions": len(items),
        "question_chars": round(statistics.mean(len(item["question"]) for item in items)),
        "option_chars": round(
            statistics.mean(len(o["answer"]) for item in items for o in item["options"])
        ),
        # About 25% when the correct option's length gives nothing away.
        "correct_is_longest": f"{100 * longest / len(items):.0f}%",
        "with_example": f"{100 * sum('```' in item['question'] for item in items) / len(items):.0f}%",
    }


async def review(llm, item: dict) -> dict:
    text = prompt("question_review").format(
        level=item["level"],
        topic=item["topic"],
        question=item["question"],
        options=options_text(item),
    )
    result = await llm.ainvoke([HumanMessage(content=text)])

    return {"id": item["id"], **result.model_dump()}


def summary(reviews: list[dict]) -> dict:
    share = lambda key: f"{100 * sum(r[key] for r in reviews) / len(reviews):.0f}%"
    mean = lambda key: round(statistics.mean(r[key] for r in reviews), 2)

    return {
        "reviewed": len(reviews),
        "key_correct": share("key_correct"),
        "single_correct": share("single_correct"),
        "distractors": mean("distractors"),
        "clarity": mean("clarity"),
        "relevance": mean("relevance"),
    }


def compare(reviews: list[dict], items: dict[str, dict]) -> None:
    """Against what's known: the traps' expected keys, or the reference verdicts."""
    expected = [r for r in reviews if "expected_key_correct" in items[r["id"]]]

    if expected:
        caught = sum(r["key_correct"] == items[r["id"]]["expected_key_correct"] for r in expected)
        print(f"traps caught: {caught} of {len(expected)}")

    reference_path = DATASETS / "reviews.json"

    if not reference_path.exists():
        return

    reference = {r["id"]: r for r in load(reference_path)["reviews"]}
    shared = [r for r in reviews if r["id"] in reference]

    if shared:
        same = sum(r["key_correct"] == reference[r["id"]]["key_correct"] for r in shared)
        print(f"agrees with the reference judge on the key: {same} of {len(shared)}")


async def main(
    path: str, sample: int | None, save_reference: bool, compare_reference: bool
) -> None:
    items = question_items(EVALS / path)
    print("measured:", measure(items))
    chosen = random.Random(7).sample(items, sample) if sample and sample < len(items) else items
    llm = judge().with_structured_output(Review)
    limit = asyncio.Semaphore(8)

    async def one(item):
        async with limit:
            return await review(llm, item)

    reviews = await asyncio.gather(*(one(item) for item in chosen))
    print(f"judged by {JUDGE_MODEL} ({JUDGE_EFFORT}):", summary(reviews))
    name = path.replace("/", "_").removesuffix(".json")
    save(RESULTS / f"reviews_{name}_{JUDGE_MODEL}_{JUDGE_EFFORT}.json", reviews)

    if save_reference:
        save(
            DATASETS / "reviews.json",
            {
                "about": f"Reference verdicts on {path} by {JUDGE_MODEL} ({JUDGE_EFFORT}).",
                "reviews": reviews,
            },
        )

    if compare_reference or any("expected_key_correct" in item for item in chosen):
        compare(reviews, {item["id"]: item for item in items})

    for r in reviews:
        if not r["key_correct"] or not r["single_correct"]:
            print(f"- {r['id']}: {r['issue']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="a question file, relative to evals/")
    parser.add_argument("--sample", type=int)
    parser.add_argument("--save-reference", action="store_true")
    parser.add_argument("--compare-reference", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(args.path, args.sample, args.save_reference, args.compare_reference))
