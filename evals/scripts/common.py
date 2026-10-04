"""What every offline test shares: where the datasets live, model prices, the judge prompts, and
one format for a question wherever it comes from."""

import json
import os
from pathlib import Path

from langchain_openai import ChatOpenAI

EVALS = Path(__file__).resolve().parents[1]
DATASETS = EVALS / "datasets"
RESULTS = EVALS / "results"
JUDGES = EVALS / "judges"

# USD per million input and output tokens (OpenAI's pricing page, October 2026).
PRICES = {
    "gpt-6-luna": (0.10, 0.50),
    "gpt-6.1-sol": (2.00, 10.00),
    "gpt-6-astra": (10.00, 50.00),
}
# The judge: stronger than what it judges, and thinking hard, so its verdicts are the reference.
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gpt-6.1-sol")
JUDGE_EFFORT = os.environ.get("JUDGE_EFFORT", "high")


def load(path: Path):
    return json.loads(path.read_text())


def save(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")


def prompt(name: str) -> str:
    """A judge or writer prompt from judges/, filled in with str.format."""
    return (JUDGES / f"{name}.md").read_text()


def model(name: str, effort: str, timeout: int = 300) -> ChatOpenAI:
    """A reasoning model takes no temperature; one with reasoning off gets a little."""
    if effort == "none":
        return ChatOpenAI(
            model=name, reasoning_effort="none", temperature=0.3, max_retries=3, timeout=timeout
        )

    return ChatOpenAI(model=name, reasoning_effort=effort, max_retries=3, timeout=timeout)


def judge() -> ChatOpenAI:
    return model(JUDGE_MODEL, JUDGE_EFFORT)


def cost(model_name: str, usage: dict) -> float:
    """USD for one call's usage metadata."""
    price_in, price_out = PRICES[model_name]

    return (
        usage.get("input_tokens", 0) * price_in + usage.get("output_tokens", 0) * price_out
    ) / 1e6


def correct_option(item: dict) -> str:
    return next(option["answer"] for option in item["options"] if option["correct"])


def options_text(item: dict) -> str:
    return "\n".join(
        f"- {option['answer']}{' [correct]' if option['correct'] else ''}"
        for option in item["options"]
    )


def question_items(path: Path) -> list[dict]:
    """Questions as a list of {id, domain, level, topic, question, options, ...}, from a dataset
    or from a results file of generate_kits.py, which use the same format."""
    data = load(path)

    return data["items"] if isinstance(data, dict) else data
