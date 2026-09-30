import uuid

from langchain_core.callbacks import get_usage_metadata_callback
from langgraph.types import Command

from app.constants.generation import MAX_CONCURRENCY, RECURSION_LIMIT
from app.constants.kinds import GenerationKind
from app.constants.statuses import Status
from app.helpers.payload import build_preparation
from app.helpers.progress import track_progress
from app.helpers.usage import merge_usage
from app.integrations import library
from app.models.generation import Generation
from app.storage import generations


async def run_pipeline(graph, generation: Generation, resume: dict | None) -> None:
    """Runs the graph until it pauses for review or finishes, keeping the row up to date."""
    config = {
        "configurable": {"thread_id": str(generation.id)},
        "max_concurrency": MAX_CONCURRENCY,
        "recursion_limit": RECURSION_LIMIT,
    }

    if resume is not None:
        graph_input = Command(resume=resume)
    elif (await graph.aget_state(config)).values:
        # A checkpoint exists, so continue from it after a crash or a retry.
        graph_input = None
    else:
        graph_input = {"input_text": generation.text}

    await generations.update(generation.id, status=Status.RUNNING, error=None)
    previous_usage = dict(generation.usage or {})

    # Counts the tokens of every LLM call in this run, including the parallel branches.
    with get_usage_metadata_callback() as tokens:
        try:
            await stream_graph(graph, generation, graph_input, config, previous_usage, tokens)
        finally:
            # Also on failure: a failed run still cost money.
            usage = merge_usage(previous_usage, tokens.usage_metadata)
            await generations.update(generation.id, usage=usage)


async def stream_graph(
    graph, generation: Generation, graph_input, config: dict, previous_usage: dict, tokens
) -> None:
    progress = dict(generation.progress or {})

    async for chunk in graph.astream(graph_input, config, stream_mode="updates"):
        if "__interrupt__" in chunk:
            topics = chunk["__interrupt__"][0].value["topics"]
            await generations.update(generation.id, status=Status.AWAITING_REVIEW, topics=topics)

            return

        if track_progress(progress, chunk):
            usage = merge_usage(previous_usage, tokens.usage_metadata)
            await generations.update(generation.id, progress=progress, usage=usage)

    values = (await graph.aget_state(config)).values
    owner_id = (
        str(generation.company_id)
        if generation.kind == GenerationKind.INTERVIEW
        else generation.owner_uid
    )
    payload = build_preparation(owner_id, generation.text, values)

    if generation.kind == GenerationKind.INTERVIEW:
        set_id: uuid.UUID = await library.create_interview(payload)
    else:
        set_id = await library.create_preparation(payload)

    await generations.update(generation.id, status=Status.DONE, preparation_id=set_id)
