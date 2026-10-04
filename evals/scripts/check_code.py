"""Runs the Python in "what does this print" questions and checks the marked answer against the
real output: ground truth for code questions, at no AI cost.

    evals/run.sh generation check_code.py datasets/questions.json

Only self-contained examples that print something are checked; ones whose output depends on the
machine (memory addresses) or need a package that isn't installed are skipped."""

import argparse
import re
import subprocess
import sys

from common import EVALS, correct_option, question_items

BLOCK = re.compile(r"```[\w+-]*\n([\s\S]*?)```")
ASKS_OUTPUT = re.compile(r"print|output|displayed", re.IGNORECASE)


def run(code: str) -> str | None:
    """What it prints; on an error, also the error's name, as an option would give it."""
    try:
        done = subprocess.run(
            [sys.executable, "-I", "-c", code],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None

    if done.returncode == 0:
        return done.stdout

    lines = done.stderr.strip().splitlines()

    return (done.stdout + " " + (lines[-1].split(":")[0] if lines else "")).strip()


def words(text: str) -> list[str]:
    """The words, without the punctuation an option adds around printed values."""
    for mark in "`,\"'":
        text = text.replace(mark, " ")

    return [word.rstrip(".;:") for word in text.split() if word.rstrip(".;:")]


def matches(output: str, option: str) -> bool:
    """The printed values appear in the option, in order ("False, then done" for False / done)."""
    remaining = iter(words(option))

    return all(any(word == other for other in remaining) for word in words(output))


def main(path: str) -> None:
    checked, right, wrong = 0, 0, []

    for item in question_items(EVALS / path):
        blocks = BLOCK.findall(item["question"])
        prose = BLOCK.sub("", item["question"])

        if len(blocks) != 1 or "print(" not in blocks[0] or not ASKS_OUTPUT.search(prose):
            continue

        output = run(blocks[0])

        if not output or not output.strip() or " at 0x" in output:
            continue

        # Not Python (a shell script), or a package this machine doesn't have.
        if "SyntaxError" in output or "ModuleNotFoundError" in output:
            continue

        checked += 1

        if matches(output, correct_option(item)):
            right += 1
        else:
            wrong.append((item["id"], " ".join(output.split()), correct_option(item)))

    print(f"ran {checked} print-questions; the marked answer matches the real output in {right}")

    for item_id, got, marked in wrong:
        print(f"- {item_id}: marked {marked!r}, real output {got!r}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="a question file, relative to evals/")
    main(parser.parse_args().path)
