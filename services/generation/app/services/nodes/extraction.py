from langchain_core.messages import HumanMessage, SystemMessage

from app.integrations import llm, tavily
from app.models.state import State
from app.prompts.extraction import (
    COMPANY_SEARCH_QUERY,
    COMPANY_SUMMARY_SYSTEM,
    EXTRACTION_SYSTEM,
)
from app.schemas.extraction import JobExtraction


async def extract_info(state: State) -> dict:
    structured_llm = llm.get_llm().with_structured_output(JobExtraction)
    result: JobExtraction = await structured_llm.ainvoke(
        [
            SystemMessage(content=EXTRACTION_SYSTEM),
            HumanMessage(content=state["input_text"]),
        ]
    )

    return {
        "title": result.title,
        "company_name": result.company_name,
        "company_description": result.company_description,
        "requirements": result.requirements,
        "level": result.level,
    }


def needs_company_search(state: State) -> str:
    has_description = bool(state.get("company_description", "").strip())
    has_name = bool(state.get("company_name", "").strip())

    return "search_company" if (not has_description and has_name) else "generate_topics"


async def search_company(state: State) -> dict:
    query = COMPANY_SEARCH_QUERY.format(company_name=state["company_name"])
    response = await tavily.get_tavily().search(query=query, max_results=3)
    snippets = [result.get("content", "") for result in response.get("results", [])]
    combined = "\n\n".join(snippets)

    message = await llm.get_llm().ainvoke(
        [
            SystemMessage(content=COMPANY_SUMMARY_SYSTEM),
            HumanMessage(content=combined or "No information found."),
        ]
    )

    return {"company_description": message.content}
