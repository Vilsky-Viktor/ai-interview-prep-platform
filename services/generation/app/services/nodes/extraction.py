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
    model = llm.get_generation_llm(state.get("kind"), None, state.get("free_kit", False))
    cached = await draft_cache.get("extraction", source, model)

    if cached is not None:
        return cached

    result: JobExtraction = await model.with_structured_output(JobExtraction).ainvoke(
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
    await draft_cache.put("extraction", source, extracted, model)

    return extracted
