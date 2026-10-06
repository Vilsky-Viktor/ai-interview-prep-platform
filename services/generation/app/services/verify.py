import logging
from collections import Counter
from uuid import UUID

from langchain_core.messages import HumanMessage

from app.constants.quality import QualityFlag
from app.helpers.prompts import bullet_list
from app.integrations import library, llm
from app.prompts.verify import VERIFY_PROMPT
from app.schemas.regenerate import QuestionContext, RegeneratedOption, RegeneratedQuestion
from app.schemas.verify import KeyCheck, QuestionQuality
from app.services.nodes.answers import generate_answers
from app.services.regenerate import regenerate
from app.storage import key_checks

logger = logging.getLogger(__name__)


async def replace(question_id: UUID, context: QuestionContext) -> None:
    if await regenerate(question_id, context) is None:
        logger.warning("Couldn't write a replacement for question %s", question_id)


def marked_answer(question: QuestionQuality) -> str:
    """The option the question marks as correct."""
    return next(option.answer for option in question.options if option.correct)


def option_order(question: QuestionQuality) -> list[int]:
    """The marked option first, so the model doesn't take a position as a hint."""
    marked = next(i for i, option in enumerate(question.options) if option.correct)

    return [marked] + [i for i in range(len(question.options)) if i != marked]


def key_check_prompt(question: QuestionQuality, context: QuestionContext) -> str:
    return VERIFY_PROMPT.format(
        level=context.level,
        topic=context.topic,
        question=question.text,
        options="\n".join(
            f"{number}. {question.options[i].answer} "
            f"(picked {question.option_picks.get(question.options[i].answer, 0)} times)"
            for number, i in enumerate(option_order(question))
        ),
        # Reasons only, counted: a reporter's free-text comment never reaches the model, so it
        # can't steer which answer counts as correct.
        reports=bullet_list(
            [
                f"{reason}: {count}"
                for reason, count in Counter(r.reason for r in question.reports).items()
            ]
        )
        or "None",
    )


async def apply_key_check(
    question_id: UUID, question: QuestionQuality, context: QuestionContext, result: KeyCheck
) -> None:
    """Keeps the question, moves the key to the right option, or replaces a broken question."""
    order = option_order(question)

    if result.correct_index is None or not 0 <= result.correct_index < len(order):
        await replace(question_id, context)

        return

    correct = order[result.correct_index]

    if correct == order[0]:
        await library.keep_question(question_id)

        return

    options = [
        RegeneratedOption(answer=option.answer, correct=i == correct)
        for i, option in enumerate(question.options)
    ]
    await library.replace_question(
        question_id, RegeneratedQuestion(text=question.text, options=options)
    )


async def check_key(question_id: UUID, question: QuestionQuality, context: QuestionContext) -> None:
    """The key check right away; used when a batched check came back unusable."""
    result: KeyCheck = (
        await llm.get_verifier_llm()
        .with_structured_output(KeyCheck)
        .ainvoke([HumanMessage(content=key_check_prompt(question, context))])
    )
    await apply_key_check(question_id, question, context, result)


async def new_options(
    question_id: UUID, question: QuestionQuality, context: QuestionContext
) -> None:
    """The same question with new options; one that turns out ambiguous is replaced."""
    result = await generate_answers(
        {
            "topic_index": 0,
            "topic": context.topic,
            "start": 0,
            "questions": [question.text],
            "level": context.level,
            "language": context.language,
        }
    )
    options = result["answer_pool"][0]["options"][0]

    if not options:
        await replace(question_id, context)

        return

    await library.replace_question(
        question_id, RegeneratedQuestion(text=question.text, options=options)
    )


async def verify(question_id: UUID, flag: QualityFlag, now: bool = False) -> None:
    """Acts on a question the library flagged from its answers and feedback; `now` checks a
    wrong key right away (a superadmin's "Fix now"). The library's current flag wins over the
    one sent: the question may have been kept, replaced or flagged otherwise since."""
    context = await library.get_question_context(question_id)
    question = await library.get_question_quality(question_id)

    # Deleted, kept or replaced since it was flagged.
    if context is None or question is None or question.flag is None:
        return

    flag = question.flag

    if flag == QualityFlag.WRONG_KEY and now:
        # Checked now, so a check still waiting in a batch is dropped: its result would come
        # after this one's.
        await key_checks.remove([question_id])
        await check_key(question_id, question, context)
    elif flag == QualityFlag.WRONG_KEY:
        # Nobody waits on it, so it goes in the next OpenAI batch at half price.
        await key_checks.add(question_id, question.text, marked_answer(question))
    elif flag == QualityFlag.WEAK_OPTIONS:
        await new_options(question_id, question, context)
    else:
        await replace(question_id, context)
