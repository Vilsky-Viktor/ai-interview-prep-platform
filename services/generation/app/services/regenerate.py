from uuid import UUID

from langchain_core.messages import HumanMessage

from app.constants.generation import REGENERATE_ATTEMPTS
from app.helpers.prompts import bullet_list
from app.helpers.questions import normalize
from app.integrations import library, llm
from app.prompts.regenerate import REGENERATE_PROMPT
from app.schemas.questions import NewQuestion
from app.schemas.regenerate import QuestionContext, RegeneratedOut, RegeneratedQuestion
from app.services.nodes.answers import generate_answers


async def new_question(context: QuestionContext) -> str | None:
    """A question that is not a duplicate of any existing one in the topic."""
    structured_llm = llm.get_question_llm().with_structured_output(NewQuestion)
    existing = list(context.existing)
    taken = {normalize(text) for text in existing}

    for _ in range(REGENERATE_ATTEMPTS):
        prompt = REGENERATE_PROMPT.format(
            level=context.level,
            topic=context.topic,
            subtopics=", ".join(context.subtopics) or context.topic,
            existing=bullet_list(existing),
        )
        result: NewQuestion = await structured_llm.ainvoke([HumanMessage(content=prompt)])
        text = result.question.strip()

        if text and normalize(text) not in taken:
            return text

        existing.append(text)

    return None


async def regenerate(question_id: UUID, context: QuestionContext) -> RegeneratedOut | None:
    """Writes a new question with its answer and options and saves it in place of the old one."""
    text = await new_question(context)

    if text is None:
        return None

    result = await generate_answers(
        {
            "topic_index": 0,
            "topic": context.topic,
            "start": 0,
            "questions": [text],
            "level": context.level,
            "company_description": "",
        }
    )
    answered = result["answer_pool"][0]

    if not answered["answers"][0]:
        return None

    await library.replace_question(
        question_id,
        RegeneratedQuestion(
            text=text, reference_answer=answered["answers"][0], options=answered["options"][0]
        ),
    )

    return RegeneratedOut(id=question_id, text=text)
