import asyncio

import httpx
import openai
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

MODEL = "gpt-6.1-sol"
# A reply that never comes.
HANG = "hang"


def reply(input_tokens: int, output_tokens: int, model: str = MODEL) -> AIMessage:
    """A model's answer with the usage it reports."""
    usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
    }

    return AIMessage(content="ok", usage_metadata=usage, response_metadata={"model_name": model})


def refused(code: str) -> openai.RateLimitError:
    """OpenAI's 429: its rate limit, or the account out of money ("insufficient_quota")."""
    response = httpx.Response(429, request=httpx.Request("POST", "https://api.openai.com"))

    return openai.RateLimitError("Refused", response=response, body={"code": code})


class Chat(BaseChatModel):
    """A chat model answering with `replies` in turn: a message, an error it raises, or HANG.
    Its calls report to LangChain's callbacks as a real model's do."""

    model: str = MODEL
    replies: list

    @property
    def _llm_type(self) -> str:
        return "fake"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        raise NotImplementedError

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        answer = self.replies.pop(0)

        if answer == HANG:
            await asyncio.sleep(3600)

        if isinstance(answer, BaseException):
            raise answer

        return ChatResult(generations=[ChatGeneration(message=answer)])
