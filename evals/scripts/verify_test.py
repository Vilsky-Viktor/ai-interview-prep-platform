"""Tests verifier settings with the service's own key-check prompt: on datasets/key_traps.json
(the key moved to a wrong option) it should find the right option, and on the same questions with
their real key it should keep the key. Questions the reference judge found flawed are left out.

    evals/run.sh generation verify_test.py gpt-6.1-sol/low gpt-6.1-sol/medium

Each question is checked as the verifier sees it after two "wrong answer" reports. Costs about
$0.001 a check on gpt-6.1-sol (120 checks a setting, about $0.11); the service's batched checks
cost half."""

import argparse
import asyncio
import time

from common import DATASETS, RESULTS, correct_option, cost, load, model, save
from langchain_core.messages import HumanMessage

from app.prompts.verify import VERIFY_PROMPT
from app.schemas.verify import KeyCheck

REPORTS = "- wrong_answer: \n- wrong_answer: "


def cases() -> list[dict]:
    """Every trap, and the same question with its real key, as {item, expected answer}."""
    originals = {item["id"]: item for item in load(DATASETS / "questions.json")["items"]}
    flawed = {
        r["id"]
        for r in load(DATASETS / "reviews.json")["reviews"]
        if not r["key_correct"] or not r["single_correct"]
    }
    found = []

    for trap in load(DATASETS / "key_traps.json")["items"]:
        original = originals[trap["id"].removeprefix("trap-")]

        if original["id"] in flawed:
            continue

        right = correct_option(original)
        found.append({"kind": "trap", "item": trap, "right": right})
        found.append({"kind": "real key", "item": original, "right": right})

    return found


def prompt_for(item: dict) -> tuple[str, list[str]]:
    """The prompt, and the options in the order shown: the marked one first, as the service does."""
    marked = [o["answer"] for o in item["options"] if o["correct"]]
    shown = marked + [o["answer"] for o in item["options"] if not o["correct"]]
    text = VERIFY_PROMPT.format(
        level=item["level"],
        topic=item["topic"],
        question=item["question"],
        options="\n".join(f"{n}. {answer} (picked 0 times)" for n, answer in enumerate(shown)),
        reports=REPORTS,
    )

    return text, shown


async def check(checker, case: dict) -> dict:
    text, shown = prompt_for(case["item"])
    started = time.monotonic()
    result = await checker.ainvoke([HumanMessage(content=text)])
    seconds = time.monotonic() - started
    index = result["parsed"].correct_index if result["parsed"] else None
    picked = shown[index] if index is not None and 0 <= index < len(shown) else None

    if picked == case["right"]:
        outcome = "right"
    elif picked is None:
        # The service replaces the question: safe, but a good question is lost when the key was right.
        outcome = "replaced"
    else:
        outcome = "wrong key"

    usage = result["raw"].usage_metadata or {}
    name = result["raw"].response_metadata["model_name"].split("-20")[0]

    return {
        "id": case["item"]["id"],
        "kind": case["kind"],
        "outcome": outcome,
        "seconds": seconds,
        "cost": cost(name, usage),
    }


def report(setting: str, results: list[dict]) -> None:
    for kind in ("trap", "real key"):
        rows = [r for r in results if r["kind"] == kind]
        counts = {
            o: sum(r["outcome"] == o for r in rows) for o in ("right", "replaced", "wrong key")
        }
        print(
            f"{setting} {kind}s: {counts['right']} of {len(rows)} right, "
            f"{counts['replaced']} replaced, {counts['wrong key']} left with a wrong key"
        )

    times = sorted(r["seconds"] for r in results)
    per_check = sum(r["cost"] for r in results) / len(results)
    print(f"{setting}: median {times[len(times) // 2]:.1f}s; ${per_check:.4f} a check", flush=True)

    for r in results:
        if r["outcome"] != "right":
            print(f"  - {r['id']} ({r['kind']}): {r['outcome']}")


async def main(settings: list[str]) -> None:
    found = cases()
    print(
        f"{len(found)} checks: {len(found) // 2} traps and the same questions with their real key"
    )

    for setting in settings:
        name, effort = setting.split("/")
        checker = model(name, effort).with_structured_output(KeyCheck, include_raw=True)
        limit = asyncio.Semaphore(8)

        async def one(case, checker=checker, limit=limit):
            async with limit:
                return await check(checker, case)

        results = await asyncio.gather(*(one(case) for case in found))
        save(RESULTS / f"verify_{setting.replace('/', '_')}.json", results)
        report(setting, results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("settings", nargs="+", help="model/effort")
    asyncio.run(main(parser.parse_args().settings))
