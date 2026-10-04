"""Generates whole kits from datasets/inputs.json through the real pipeline (extraction, topics,
every topic approved, questions, fill), and reports cost, time and tokens. Nothing is saved to a
library. Question reuse and the draft cache are off, so every run makes every call itself.

    evals/run.sh generation generate_kits.py python_backend senior_accountant
    MODEL=gpt-6-luna EFFORT=low evals/run.sh generation generate_kits.py --all --label luna
    OVERSAMPLE=1.0 evals/run.sh generation generate_kits.py python_backend --label oversample-1.0

Writes results/kit_<domain>_<label>.json in the question format the other scripts read. Costs
about $1.60-2.30 a kit on gpt-6.1-sol (7-10 topics), $0.05 on gpt-6-luna."""

import argparse
import asyncio
import os
import time
import uuid

from common import DATASETS, RESULTS, cost, generation_models, load, save
from langchain_core.callbacks import get_usage_metadata_callback
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

import app.helpers.questions as question_helpers
import app.services.graph as graph_module
import app.services.nodes.fill as fill_node
import app.services.nodes.questions as questions_node
from app.config.settings import settings
from app.constants.generation import MAX_CONCURRENCY, RECURSION_LIMIT
from app.constants.kinds import GenerationKind
from app.storage import draft_cache


async def no_reuse(state):
    return {"topic_embeddings": [], "reused": [[] for _ in state["topics"]]}


async def no_cache(*_args):
    return None


def tune(fill_calls: list) -> None:
    """OVERSAMPLE replaces QUESTION_OVERSAMPLE everywhere it's read, and every call that tops up a
    short topic is counted: what a lower oversample saves, the fill-ups pay back, one at a time."""
    if "OVERSAMPLE" in os.environ:
        for module in (questions_node, fill_node, question_helpers):
            module.QUESTION_OVERSAMPLE = float(os.environ["OVERSAMPLE"])

    generate_questions = fill_node.generate_questions

    async def counted(task):
        fill_calls.append(task["topic"])

        return await generate_questions(task)

    fill_node.generate_questions = counted


async def generate(domain: dict, fill_calls: list) -> tuple[list[dict], dict]:
    graph = graph_module.build_graph(InMemorySaver())
    config = {
        "configurable": {"thread_id": str(uuid.uuid4())},
        "max_concurrency": MAX_CONCURRENCY,
        "recursion_limit": RECURSION_LIMIT,
    }
    started = time.monotonic()

    with get_usage_metadata_callback() as usage:
        await graph.ainvoke(
            {
                "input_text": domain["text"],
                "language": "en",
                "kind": GenerationKind.PREPARATION.value,
            },
            config,
        )
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
        "fill_calls": len(fill_calls),
        **totals,
    }

    return items, run


async def main(domain_ids: list[str], label: str) -> None:
    models = generation_models(settings)
    fill_calls = []
    tune(fill_calls)
    graph_module.find_reused = no_reuse
    draft_cache.get = no_cache
    draft_cache.put = no_cache
    domains = {domain["id"]: domain for domain in load(DATASETS / "inputs.json")["domains"]}

    for domain_id in domain_ids:
        fill_calls.clear()
        items, run = await generate(domains[domain_id], fill_calls)
        run["model"] = models
        run["oversample"] = questions_node.QUESTION_OVERSAMPLE
        save(RESULTS / f"kit_{domain_id}_{label}.json", {"run": run, "items": items})
        print(
            f"{domain_id}: {run['topics']} topics, {run['questions']} questions, {run['seconds']}s, "
            f"${run['cost']:.3f} (${run['cost'] / max(run['topics'], 1):.4f} a topic), "
            f"{run['fill_calls']} fill-up calls",
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
