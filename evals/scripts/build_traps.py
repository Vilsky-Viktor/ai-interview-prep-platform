"""Builds datasets/key_traps.json from datasets/questions.json, with no AI cost: questions whose
answer key is moved to a wrong option on purpose. A judge or the verifier that's any good must
catch them; review_questions.py reports how many it does.

With --multi, builds datasets/multi_key_traps.json from the multi-answer ("select all that apply")
questions of datasets/multi_questions.json: one option's mark flipped, so the key still marks 2 or
3 options and looks like a real one, but one option is wrong.

Runs anywhere with Python: evals/run.sh generation build_traps.py [--count 60] [--multi]"""

import argparse
import random

from common import DATASETS, is_multi, load, save


def trap(item: dict, rng: random.Random) -> dict:
    """The same question, the key on one of its wrong options instead."""
    wrong = rng.choice(
        [index for index, option in enumerate(item["options"]) if not option["correct"]]
    )
    options = [
        {"answer": option["answer"], "correct": index == wrong}
        for index, option in enumerate(item["options"])
    ]

    return {**item, "id": f"trap-{item['id']}", "options": options, "expected_key_correct": False}


def multi_trap(item: dict, rng: random.Random) -> dict:
    """The same multi-answer question with one option's mark flipped, so it still looks like a
    real key of 2 or 3 options: with 2 marked, a wrong one marked too; with 3, a right one
    unmarked."""
    marked = [index for index, option in enumerate(item["options"]) if option["correct"]]
    flippable = [
        index
        for index, option in enumerate(item["options"])
        if option["correct"] == (len(marked) > 2)
    ]
    flipped = rng.choice(flippable)
    options = [
        {"answer": option["answer"], "correct": option["correct"] != (index == flipped)}
        for index, option in enumerate(item["options"])
    ]

    return {**item, "id": f"trap-{item['id']}", "options": options, "expected_key_correct": False}


def main(count: int, multi: bool) -> None:
    source = "multi_questions.json" if multi else "questions.json"
    items = load(DATASETS / source)["items"]

    if multi:
        items = [item for item in items if is_multi(item)]

    rng = random.Random(7)
    # Spread over every domain, not just the first ones.
    chosen = rng.sample(items, min(count, len(items)))
    save(
        DATASETS / ("multi_key_traps.json" if multi else "key_traps.json"),
        {
            "about": f"Questions from {source} with the answer key changed to a wrong one on "
            "purpose (expected_key_correct is false). Ground truth for judges and the verifier.",
            "items": [(multi_trap if multi else trap)(item, rng) for item in chosen],
        },
    )
    print(f"{len(chosen)} traps")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=60)
    parser.add_argument("--multi", action="store_true")
    args = parser.parse_args()
    main(args.count, args.multi)
