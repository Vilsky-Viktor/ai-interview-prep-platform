from langchain_core.messages import HumanMessage, SystemMessage

from app.helpers.prompts import language_name
from app.integrations import llm
from app.models.state import State
from app.prompts.extraction import EXTRACTION_SYSTEM
from app.schemas.extraction import JobExtraction
from app.storage import draft_cache


async def extract_info(state: State) -> dict:
    """Title, requirements and level; the same pasted text reuses its earlier result."""
    system = EXTRACTION_SYSTEM.format(language=language_name(state.get("language")))
    source = system + state["input_text"]
    cached = await draft_cache.get("extraction", source)

    if cached is not None:
        return cached

    structured_llm = llm.get_generation_llm().with_structured_output(JobExtraction)
    result: JobExtraction = await structured_llm.ainvoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=state["input_text"]),
        ]
    )

    extracted = {
        "title": result.title,
        "requirements": result.requirements,
        "level": result.level,
    }
    await draft_cache.put("extraction", source, extracted)

    return extracted
