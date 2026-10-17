"""Measures a set of questions, and has the judge review them with judges/question_review.md.

    evals/run.sh generation review_questions.py datasets/questions.json [--sample 40]
    evals/run.sh generation review_questions.py datasets/key_traps.json        # catch rate
    evals/run.sh generation review_questions.py datasets/multi_questions.json  # multi-answer
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
    correct_options,
    is_multi,
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
    key_correct: bool = Field(
        description="The options marked correct are exactly the ones that are correct"
    )
    # Named for single-answer questions, where it means exactly one defensible option; for a
    # multi-answer one, every option is clearly right or clearly wrong.
    single_correct: bool = Field(description="The key can't be argued (see the prompt)")
    distractors: int = Field(ge=1, le=5, description="How tempting the wrong options are")
    clarity: int = Field(ge=1, le=5, description="How clear and unambiguous the question is")
    relevance: int = Field(ge=1, le=5, description="How useful it is at this level")
    seconds: int = Field(description="Seconds a capable candidate needs to read and answer it")
    issue: str = Field(description="The main problem in a few words, or empty")


def longest_is_correct(items: list[dict]) -> str:
    """How often the longest option is a correct one, and how often it would be if length gave
    nothing away: 25% with one correct option of four, the share of correct options with more."""
    longest = chance = 0

    for item in items:
        sizes = [len(option["answer"]) for option in item["options"]]
        longest += any(
            option["correct"]
            and len(option["answer"]) == max(sizes)
            and sizes.count(max(sizes)) == 1
            for option in item["options"]
        )
        chance += len(correct_options(item)) / len(item["options"])

    return f"{100 * longest / len(items):.0f}% (by chance {100 * chance / len(items):.0f}%)"


def measure(items: list[dict]) -> dict:
    """What can be counted without a judge; single- and multi-answer questions apart."""
    single = [item for item in items if not is_multi(item)]
    multi = [item for item in items if is_multi(item)]
    measured = {
        "questions": len(items),
        "multi_answer": len(multi),
        "question_chars": round(statistics.mean(len(item["question"]) for item in items)),
        "option_chars": round(
            statistics.mean(len(o["answer"]) for item in items for o in item["options"])
        ),
        "with_example": f"{100 * sum('```' in item['question'] for item in items) / len(items):.0f}%",
    }

    if single:
        # About 25% when the correct option's length gives nothing away.
        measured["correct_is_longest"] = longest_is_correct(single)

    if multi:
        measured["multi_correct_is_longest"] = longest_is_correct(multi)
        measured["multi_correct_counts"] = {
            n: sum(len(correct_options(item)) == n for item in multi) for n in (2, 3)
        }

    return measured


async def review(llm, item: dict) -> dict:
    text = prompt("question_review").format(
        level=item["level"],
        topic=item["topic"],
        question=item["question"],
        options=options_text(item),
    )
    result = await llm.ainvoke([HumanMessage(content=text)])

    return {"id": item["id"], **result.model_dump()}


def summary(reviews: list[dict], items: dict[str, dict]) -> dict:
    share = lambda rows, key: f"{100 * sum(r[key] for r in rows) / len(rows):.1f}%"
    mean = lambda key: round(statistics.mean(r[key] for r in reviews), 2)
    result = {
        "reviewed": len(reviews),
        "key_correct": share(reviews, "key_correct"),
        "single_correct": share(reviews, "single_correct"),
        "distractors": mean("distractors"),
        "clarity": mean("clarity"),
        "relevance": mean("relevance"),
    }

    # Each kind's key accuracy apart: multi-answer keys must reach the same target.
    for kind, rows in (
        ("single", [r for r in reviews if not is_multi(items[r["id"]])]),
        ("multi", [r for r in reviews if is_multi(items[r["id"]])]),
    ):
        if rows and len(rows) < len(reviews):
            result[f"{kind}_answer"] = {
                "reviewed": len(rows),
                "key_correct": share(rows, "key_correct"),
                "unarguable_key": share(rows, "single_correct"),
            }

    return result


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
    by_id = {item["id"]: item for item in items}
    print(f"judged by {JUDGE_MODEL} ({JUDGE_EFFORT}):", summary(reviews, by_id))
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
        compare(reviews, by_id)

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
