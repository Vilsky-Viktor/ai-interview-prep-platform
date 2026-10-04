from langchain_core.messages import HumanMessage

from app.integrations import llm
from app.prompts.titles import TITLE_COMPANY_PROMPT
from app.schemas.titles import TitleCheckOut


async def check_title(title: str) -> TitleCheckOut:
    """Whether a title names a company, which a public kit's title can't."""
    return (
        await llm.get_title_check_llm()
        .with_structured_output(TitleCheckOut)
        .ainvoke([HumanMessage(content=TITLE_COMPANY_PROMPT.format(title=title))])
    )
