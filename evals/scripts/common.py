"""What every offline test shares: where the datasets live, model prices, the judge prompts, and
one format for a question wherever it comes from."""

import json
import os
from pathlib import Path

from langchain_openai import ChatOpenAI
from prepza_common.llm import call_cost

EVALS = Path(__file__).resolve().parents[1]
DATASETS = EVALS / "datasets"
RESULTS = EVALS / "results"
JUDGES = EVALS / "judges"

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


def generation_models(settings) -> str:
    """With MODEL and EFFORT set, the model under test writes the tests; without them the
    service's own setting is tested. Returns what writes them, for the results."""
    names = ("interview",)

    for name in names:
        if "MODEL" in os.environ:
            setattr(settings, f"{name}_model", os.environ["MODEL"])

        if "EFFORT" in os.environ:
            setattr(settings, f"{name}_reasoning_effort", os.environ["EFFORT"])

    return ", ".join(
        f"{name} {getattr(settings, f'{name}_model')} ({getattr(settings, f'{name}_reasoning_effort')})"
        for name in names
    )


def judge() -> ChatOpenAI:
    return model(JUDGE_MODEL, JUDGE_EFFORT)


def cost(model_name: str, usage: dict) -> float:
    """USD for one call's usage metadata; a model without a price fails the run."""
    spent = call_cost(model_name, usage)

    if spent is None:
        raise KeyError(model_name)

    return spent


def correct_option(item: dict) -> str:
    return next(option["answer"] for option in item["options"] if option["correct"])


def correct_options(item: dict) -> set[str]:
    return {option["answer"] for option in item["options"] if option["correct"]}


def is_multi(item: dict) -> bool:
    """A select-all-that-apply question: more than one option marked correct."""
    return len(correct_options(item)) > 1


def options_text(item: dict) -> str:
    return "\n".join(
        f"- {option['answer']}{' [correct]' if option['correct'] else ''}"
        for option in item["options"]
    )


def question_items(path: Path) -> list[dict]:
    """Questions as a list of {id, domain, level, topic, question, options, ...}, from a dataset
    or from a results file of generate_tests.py, which use the same format."""
    data = load(path)

    return data["items"] if isinstance(data, dict) else data
