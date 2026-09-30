from langchain_core.messages import HumanMessage, SystemMessage

from app.helpers.scores import clamp_score
from app.integrations import llm
from app.prompts.grading import GRADING_PROMPT, GRADING_SYSTEM
from app.schemas.grade import Grade


async def grade_open_answer(question: dict, answer: str) -> Grade:
    structured_llm = llm.get_grader_llm().with_structured_output(Grade)
    prompt = GRADING_PROMPT.format(
        question=question["text"],
        reference_answer=question["reference_answer"],
        answer=answer,
    )
    grade: Grade = await structured_llm.ainvoke(
        [SystemMessage(content=GRADING_SYSTEM), HumanMessage(content=prompt)]
    )

    return Grade(score=clamp_score(grade.score), feedback=grade.feedback.strip())
