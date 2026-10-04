"""Tests tutor settings on datasets/follow_ups.json with the real tutor prompt, cheapest first, and
can stop at the first setting that answers every follow-up correctly. The judge uses
judges/tutor_review.md.

Run in the rounds container (it has the tutor prompt):
    evals/run.sh rounds tutor_test.py gpt-6-luna/low gpt-6.1-sol/low --stop-when-all-correct

Costs per follow-up: the tutor's turn (about $0.0001 on gpt-6-luna, $0.003 on gpt-6.1-sol) plus
about $0.01 for the judge."""

import argparse
import asyncio
import time

from common import DATASETS, JUDGE_MODEL, RESULTS, cost, judge, load, model, prompt, save
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.prompts.chat import CHAT_SYSTEM


class Verdict(BaseModel):
    correct: bool = Field(description="Every claim and calculation in the reply is correct")
    agrees_with_key: bool = Field(description="It doesn't contradict the marked correct answer")
    helpful: int = Field(ge=1, le=5, description="How well it answers what was asked")
    issue: str = Field(description="The error or weakness in a few words, or empty")


async def ask(tutor, item: dict, extra_rule: str) -> dict:
    """The tutor's reply, the seconds to its first word, and its cost."""
    system = CHAT_SYSTEM.format(
        question=item["question"],
        correct_answer=item["correct"],
        answer=item["picked"],
        result="Result: incorrect.",
        language="English",
    )

    if extra_rule:
        system = system.rstrip() + f"\n- {extra_rule}\n"

    started = time.monotonic()
    first, reply, usage = None, "", {}

    async for chunk in tutor.astream(
        [SystemMessage(content=system), HumanMessage(content=item["follow_up"])]
    ):
        if chunk.content and first is None:
            first = time.monotonic() - started

        reply += chunk.content or ""
        usage = chunk.usage_metadata or usage

    return {
        "reply": reply,
        "words": len(reply.split()),
        "first_word": first or 0.0,
        "cost": cost(tutor.model_name, usage),
    }


async def run_setting(setting: str, items: list[dict], judge_llm, extra_rule: str) -> list[dict]:
    name, effort = setting.split("/")
    tutor = model(name, effort, timeout=120)
    limit = asyncio.Semaphore(6)

    async def one(item):
        async with limit:
            answer = await ask(tutor, item, extra_rule)
            text = prompt("tutor_review").format(
                question=item["question"],
                correct=item["correct"],
                picked=item["picked"],
                follow_up=item["follow_up"],
                reply=answer["reply"],
            )
            verdict = await judge_llm.ainvoke([HumanMessage(content=text)])

            return {"id": item["id"], "kind": item["kind"], **answer, **verdict.model_dump()}

    return await asyncio.gather(*(one(item) for item in items))


def report(setting: str, results: list[dict]) -> bool:
    wrong = [r for r in results if not r["correct"] or not r["agrees_with_key"]]
    firsts = sorted(r["first_word"] for r in results)
    helpful = sum(r["helpful"] for r in results) / len(results)
    per_turn = sum(r["cost"] for r in results) / len(results)
    words = sorted(r["words"] for r in results)
    print(
        f"{setting}: {len(results) - len(wrong)} of {len(results)} correct; helpful {helpful:.2f}; "
        f"first word median {firsts[len(firsts) // 2]:.1f}s, slowest {firsts[-1]:.1f}s; "
        f"${per_turn:.5f} a turn; median reply {words[len(words) // 2]} words",
        flush=True,
    )

    for r in wrong:
        print(f"  - {r['id']} ({r['kind']}): {r['issue']}")

    return not wrong


async def main(settings: list[str], stop: bool, dataset: str, extra_rule: str, label: str) -> None:
    items = load(DATASETS / dataset)["items"]
    judge_llm = judge().with_structured_output(Verdict)
    print(f"{len(items)} follow-ups, judged by {JUDGE_MODEL}")

    for setting in settings:
        results = await run_setting(setting, items, judge_llm, extra_rule)
        name = dataset.removesuffix(".json").removeprefix("follow_ups")
        save(RESULTS / f"tutor{name}_{setting.replace('/', '_')}{label}.json", results)

        if report(setting, results) and stop:
            print(f"Stopping: {setting} answered every follow-up correctly.")

            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("settings", nargs="+", help="model/effort, cheapest first")
    parser.add_argument("--stop-when-all-correct", action="store_true")
    parser.add_argument("--dataset", default="follow_ups.json", help="a file in datasets/")
    parser.add_argument("--extra-rule", default="", help="a rule added to the tutor's prompt")
    parser.add_argument("--label", default="", help="added to the result file's name")
    args = parser.parse_args()
    asyncio.run(
        main(args.settings, args.stop_when_all_correct, args.dataset, args.extra_rule, args.label)
    )
