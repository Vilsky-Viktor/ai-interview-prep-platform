"""Generates whole kits from datasets/inputs.json through the real pipeline (extraction, topics,
every topic approved, questions, fill), and reports cost, time and tokens. Nothing is saved to a
library. Question reuse and the draft cache are off, so every run makes every call itself.

    evals/run.sh generation generate_kits.py python_backend senior_accountant
    MODEL=gpt-6-luna EFFORT=low evals/run.sh generation generate_kits.py --all --label luna

Writes results/kit_<domain>_<label>.json in the question format the other scripts read. Costs
about $1.60-2.30 a kit on gpt-6.1-sol (7-10 topics), $0.05 on gpt-6-luna."""

import argparse
import asyncio
import os
import time
import uuid

from common import DATASETS, RESULTS, cost, load, save
from langchain_core.callbacks import get_usage_metadata_callback
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

import app.services.graph as graph_module
from app.config.settings import settings
from app.constants.generation import MAX_CONCURRENCY, RECURSION_LIMIT
from app.integrations import llm
from app.storage import draft_cache


async def no_reuse(state):
    return {"topic_embeddings": [], "reused": [[] for _ in state["topics"]]}


async def no_cache(*_args):
    return None


async def generate(domain: dict) -> tuple[list[dict], dict]:
    graph = graph_module.build_graph(InMemorySaver())
    config = {
        "configurable": {"thread_id": str(uuid.uuid4())},
        "max_concurrency": MAX_CONCURRENCY,
        "recursion_limit": RECURSION_LIMIT,
    }
    started = time.monotonic()

    with get_usage_metadata_callback() as usage:
        await graph.ainvoke({"input_text": domain["text"], "language": "en"}, config)
        topics = (await graph.aget_state(config)).values["topics"]
        state = await graph.ainvoke(
            Command(resume={"selected": list(range(len(topics))), "instructions": ""}), config
        )

    items = [
        {
            "id": f"{domain['id']}-{ti}-{qi}",
            "domain": domain["id"],
            "level": state["level"],
            "topic": topic["topic"],
            "question": text,
            "options": options,
        }
        for ti, topic in enumerate(state.get("final") or [])
        for qi, (text, options) in enumerate(
            zip(topic["questions"], topic["answer_options"], strict=True)
        )
    ]
    totals = {"input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0, "cost": 0.0}

    for name, metadata in usage.usage_metadata.items():
        totals["input_tokens"] += metadata.get("input_tokens", 0)
        totals["output_tokens"] += metadata.get("output_tokens", 0)
        totals["reasoning_tokens"] += (metadata.get("output_token_details") or {}).get(
            "reasoning", 0
        )
        totals["cost"] += cost(name, metadata)

    run = {
        "domain": domain["id"],
        "level": state["level"],
        "topics": len(state.get("final") or []),
        "questions": len(items),
        "seconds": round(time.monotonic() - started),
        **totals,
    }

    return items, run


async def main(domain_ids: list[str], label: str) -> None:
    # The model and effort under test, unless the service's own settings are what's tested.
    settings.generation_model = os.environ.get("MODEL", settings.generation_model)
    settings.llm_reasoning_effort = os.environ.get("EFFORT", settings.llm_reasoning_effort)
    llm.get_llm.cache_clear()
    graph_module.find_reused = no_reuse
    draft_cache.get = no_cache
    draft_cache.put = no_cache
    domains = {domain["id"]: domain for domain in load(DATASETS / "inputs.json")["domains"]}

    for domain_id in domain_ids:
        items, run = await generate(domains[domain_id])
        run["model"] = f"{settings.generation_model} ({settings.llm_reasoning_effort})"
        save(RESULTS / f"kit_{domain_id}_{label}.json", {"run": run, "items": items})
        print(
            f"{domain_id}: {run['topics']} topics, {run['questions']} questions, {run['seconds']}s, "
            f"${run['cost']:.3f} (${run['cost'] / max(run['topics'], 1):.4f} a topic)",
            flush=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domains", nargs="*", help="domain ids from datasets/inputs.json")
    parser.add_argument("--all", action="store_true", help="every domain")
    parser.add_argument("--label", default="run", help="names the result files")
    args = parser.parse_args()
    chosen = (
        [d["id"] for d in load(DATASETS / "inputs.json")["domains"]] if args.all else args.domains
    )
    asyncio.run(main(chosen, args.label))
