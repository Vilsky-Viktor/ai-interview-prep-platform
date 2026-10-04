"""Tests settings for the public-title check on datasets/titles.json with the service's own prompt.
The labels are known, so no judge is needed.

    evals/run.sh generation titles_test.py gpt-6-luna/none gpt-6-luna/low gpt-6.1-sol/low

A wrongly blocked title annoys an author; a company let through breaks the rule. Costs well under
$0.01 a setting on gpt-6-luna, about $0.06 on gpt-6.1-sol."""

import argparse
import asyncio
import time

from common import DATASETS, RESULTS, cost, load, model, save
from langchain_core.messages import HumanMessage

from app.prompts.titles import TITLE_COMPANY_PROMPT
from app.schemas.titles import TitleCheckOut


async def check(checker, item: dict) -> dict:
    started = time.monotonic()
    result = await checker.ainvoke(
        [HumanMessage(content=TITLE_COMPANY_PROMPT.format(title=item["title"]))]
    )
    seconds = time.monotonic() - started
    usage = result["raw"].usage_metadata or {}
    has_company = result["parsed"].has_company if result["parsed"] else None

    return {
        **item,
        "answer": has_company,
        "seconds": seconds,
        "cost": cost(result["raw"].response_metadata["model_name"].split("-20")[0], usage),
    }


def report(setting: str, results: list[dict]) -> None:
    blocked = [r for r in results if r["answer"] is True and not r["has_company"]]
    let_through = [r for r in results if r["answer"] is False and r["has_company"]]
    failed = [r for r in results if r["answer"] is None]
    right = len(results) - len(blocked) - len(let_through) - len(failed)
    times = sorted(r["seconds"] for r in results)
    per_check = sum(r["cost"] for r in results) / len(results)
    print(
        f"{setting}: {right} of {len(results)} right; {len(blocked)} fine titles blocked, "
        f"{len(let_through)} companies let through, {len(failed)} failed; "
        f"median {times[len(times) // 2]:.1f}s, slowest {times[-1]:.1f}s; ${per_check:.6f} a check",
        flush=True,
    )

    for r in blocked + let_through + failed:
        print(f"  - {r['id']} ({r['kind']}): {r['title']!r}, answered {r['answer']}")


async def main(settings: list[str]) -> None:
    items = load(DATASETS / "titles.json")["items"]
    print(f"{len(items)} titles, {sum(i['has_company'] for i in items)} naming a company")

    for setting in settings:
        name, effort = setting.split("/")
        checker = model(name, effort, timeout=60).with_structured_output(
            TitleCheckOut, include_raw=True
        )
        limit = asyncio.Semaphore(8)

        async def one(item, checker=checker, limit=limit):
            async with limit:
                return await check(checker, item)

        results = await asyncio.gather(*(one(item) for item in items))
        save(RESULTS / f"titles_{setting.replace('/', '_')}.json", results)
        report(setting, results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("settings", nargs="+", help="model/effort")
    asyncio.run(main(parser.parse_args().settings))
