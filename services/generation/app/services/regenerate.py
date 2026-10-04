from uuid import UUID

from langchain_core.messages import HumanMessage

from app.constants.generation import REGENERATE_ATTEMPTS
from app.helpers.prompts import bullet_list, language_name
from app.helpers.questions import normalize, with_example
from app.integrations import library, llm
from app.prompts.regenerate import REGENERATE_PROMPT
from app.schemas.questions import NewQuestion
from app.schemas.regenerate import QuestionContext, RegeneratedOut, RegeneratedQuestion
from app.services.dedupe import distinct_by_meaning
from app.services.nodes.answers import generate_answers


async def new_question(context: QuestionContext) -> str | None:
    """A question that neither repeats nor rephrases any existing one in the topic."""
    structured_llm = llm.get_llm().with_structured_output(NewQuestion)
    existing = list(context.existing)
    taken = {normalize(text) for text in existing}

    for _ in range(REGENERATE_ATTEMPTS):
        prompt = REGENERATE_PROMPT.format(
            level=context.level,
            topic=context.topic,
            subtopics=", ".join(context.subtopics) or context.topic,
            existing=bullet_list(existing),
            language=language_name(context.language),
        )
        result: NewQuestion = await structured_llm.ainvoke([HumanMessage(content=prompt)])
        text = with_example(result.question, result.example)

        if text and normalize(text) not in taken:
            texts = [*context.existing, text]
            kept = await distinct_by_meaning(texts, keep_first=len(context.existing))

            if len(kept) == len(texts):
                return text

        existing.append(text)

    return None


async def regenerate(question_id: UUID, context: QuestionContext) -> RegeneratedOut | None:
    """Writes a new question with its options and saves it in place of the old one."""
    for _ in range(REGENERATE_ATTEMPTS):
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
                "language": context.language,
            }
        )
        options = result["answer_pool"][0]["options"][0]

        if options:
            await library.replace_question(
                question_id, RegeneratedQuestion(text=text, options=options)
            )

            return RegeneratedOut(id=question_id, text=text)

        # No options means the question was ambiguous; never offer it again.
        context = context.model_copy(update={"existing": [*context.existing, text]})

    return None
