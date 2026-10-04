"""Builds datasets/key_traps.json from datasets/questions.json, with no AI cost: questions whose
answer key is moved to a wrong option on purpose. A judge or the verifier that's any good must
catch them; review_questions.py reports how many it does.

Runs anywhere with Python: evals/run.sh generation build_traps.py [--count 60]"""

import argparse
import random

from common import DATASETS, load, save


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


def main(count: int) -> None:
    items = load(DATASETS / "questions.json")["items"]
    rng = random.Random(7)
    # Spread over every domain, not just the first ones.
    chosen = rng.sample(items, min(count, len(items)))
    save(
        DATASETS / "key_traps.json",
        {
            "about": "Questions from questions.json with the answer key moved to a wrong option on "
            "purpose (expected_key_correct is false). Ground truth for judges and the verifier.",
            "items": [trap(item, rng) for item in chosen],
        },
    )
    print(f"{len(chosen)} traps")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=60)
    main(parser.parse_args().count)
