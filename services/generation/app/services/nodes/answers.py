import random

from langchain_core.messages import HumanMessage
from langgraph.types import Send

from app.constants.generation import ANSWER_ATTEMPTS, ANSWER_BATCH_SIZE, DISTRACTORS
from app.helpers.prompts import company_block
from app.helpers.questions import clean_distractors
from app.integrations import llm
from app.models.state import AnswerTask, State
from app.prompts.answers import ANSWERS_PROMPT
from app.schemas.questions import AnswerList


def fan_out_answers(state: State):
    """Conditional edge: one branch per batch of ANSWER_BATCH_SIZE questions."""
    sends = []

    for ti, questions in enumerate(state.get("topic_questions", [])):
        for start in range(0, len(questions), ANSWER_BATCH_SIZE):
            task: AnswerTask = {
                "topic_index": ti,
                "topic": state["topics"][ti]["main_topic"],
                "start": start,
                "questions": questions[start : start + ANSWER_BATCH_SIZE],
                "level": state["level"],
                "company_description": state.get("company_description", ""),
            }
            sends.append(Send("generate_answers", task))

    return sends or "collect_results"


async def generate_answers(task: AnswerTask) -> dict:
    structured_llm = llm.get_llm().with_structured_output(AnswerList)
    questions = task["questions"]
    done: dict = {}
    pending = list(range(len(questions)))

    # Retry only the questions the model skipped or returned incomplete/invalid.
    for _ in range(ANSWER_ATTEMPTS):
        if not pending:
            break

        prompt = ANSWERS_PROMPT.format(
            company_block=company_block(task["company_description"]),
            level=task["level"],
            topic=task["topic"],
            distractors=DISTRACTORS,
            questions="\n".join(f"[{i}] {questions[i]}" for i in pending),
        )
        result: AnswerList = await structured_llm.ainvoke([HumanMessage(content=prompt)])

        for item in result.answers:
            if item.id not in pending:
                continue

            answer = item.answer.strip()
            correct = item.correct_option.strip()
            distractors = clean_distractors(item.distractors, correct)

            if answer and correct and len(distractors) >= DISTRACTORS:
                options = [{"answer": correct, "correct": True}] + [
                    {"answer": d, "correct": False} for d in distractors[:DISTRACTORS]
                ]
                # Avoid the correct option always being first.
                random.shuffle(options)
                done[item.id] = {"answer": answer, "options": options}

        pending = [i for i in pending if i not in done]

    return {
        "answer_pool": [
            {
                "topic_index": task["topic_index"],
                "start": task["start"],
                "answers": [done.get(i, {}).get("answer", "") for i in range(len(questions))],
                "options": [done.get(i, {}).get("options", []) for i in range(len(questions))],
            }
        ]
    }
