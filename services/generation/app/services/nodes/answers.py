import logging

from langchain_core.messages import HumanMessage
from openai import LengthFinishReasonError

from app.constants.generation import ANSWER_ATTEMPTS, DISTRACTORS, MAX_OPTION_CHARS
from app.helpers.prompts import language_name
from app.helpers.questions import build_options
from app.integrations import llm
from app.models.state import AnswerTask
from app.prompts.answers import ANSWERS_PROMPT
from app.schemas.questions import AnswerList

logger = logging.getLogger(__name__)


async def generate_answers(task: AnswerTask) -> dict:
    """Options for questions that already exist: a re-generated question, or new options for one."""
    structured_llm = llm.get_llm().with_structured_output(AnswerList)
    questions = task["questions"]
    done: dict = {}
    pending = list(range(len(questions)))

    # Retry only the questions the model skipped or returned incomplete/invalid.
    for _ in range(ANSWER_ATTEMPTS):
        if not pending:
            break

        prompt = ANSWERS_PROMPT.format(
            level=task["level"],
            topic=task["topic"],
            distractors=DISTRACTORS,
            max_chars=MAX_OPTION_CHARS,
            language=language_name(task.get("language")),
            questions="\n".join(f"[{i}] {questions[i]}" for i in pending),
        )
        try:
            result: AnswerList = await structured_llm.ainvoke([HumanMessage(content=prompt)])
        except LengthFinishReasonError:
            # The model looped until the output cap; the next attempt retries the same questions.
            logger.warning("Options for %r ran too long", task["topic"])

            continue

        for item in result.answers:
            if item.id not in pending:
                continue

            if item.ambiguous:
                # More than one defensible answer: drop it (no options) rather than retry.
                done[item.id] = []

                continue

            options = build_options(item.correct_option, item.distractors)

            # Options that don't qualify count as incomplete, so the next attempt retries them.
            if options:
                done[item.id] = options

        pending = [i for i in pending if i not in done]

    return {
        "answer_pool": [
            {
                "topic_index": task["topic_index"],
                "start": task["start"],
                "options": [done.get(i, []) for i in range(len(questions))],
            }
        ]
    }
