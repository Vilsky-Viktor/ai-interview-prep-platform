from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.constants.rounds import ChatRole
from app.helpers.chat import grade_summary, learner_answer
from app.helpers.rounds import find_question
from app.integrations import llm
from app.models.chat import ChatMessage
from app.models.rounds import Answer, Round
from app.prompts.chat import CHAT_SYSTEM


def build_messages(
    round_: Round, answer: Answer, history: list[ChatMessage], message: str
) -> list[BaseMessage]:
    question = find_question(round_, str(answer.question_id))
    system = CHAT_SYSTEM.format(
        question=question["text"],
        reference_answer=question["reference_answer"],
        answer=learner_answer(question, answer),
        grade=grade_summary(answer),
    )
    messages: list[BaseMessage] = [SystemMessage(content=system)]

    for item in history:
        message_class = HumanMessage if item.role == ChatRole.USER else AIMessage
        messages.append(message_class(content=item.content))

    messages.append(HumanMessage(content=message))

    return messages


async def stream_reply(messages: list[BaseMessage]) -> AsyncIterator[str]:
    async for chunk in llm.get_chat_llm().astream(messages):
        if chunk.content:
            yield chunk.content
