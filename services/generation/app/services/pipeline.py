import uuid
from contextlib import aclosing

from langgraph.types import Command
from prepza_common import pubsub

from app.constants.events import GENERATION_COMPLETED
from app.constants.generation import MAX_CONCURRENCY, RECURSION_LIMIT
from app.constants.kinds import GenerationKind
from app.constants.statuses import Status
from app.helpers.payload import build_preparation
from app.helpers.progress import track_progress
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
    await stream_graph(graph, generation, graph_input, config)


async def stream_graph(graph, generation: Generation, graph_input, config: dict) -> None:
    progress = dict(generation.progress or {})
    paused = False

    # aclosing stops the graph right away on cancel instead of leaving it to garbage collection.
    async with aclosing(graph.astream(graph_input, config, stream_mode="updates")) as stream:
        async for chunk in stream:
            # Stop spending tokens as soon as the user cancels.
            if await generations.is_cancelled(generation.id):
                return

            # The stream ends by itself after an interrupt; leaving early would abort the run.
            if "__interrupt__" in chunk:
                topics = chunk["__interrupt__"][0].value["topics"]
                await generations.update(
                    generation.id, status=Status.AWAITING_REVIEW, topics=topics
                )
                paused = True

                continue

            if track_progress(progress, chunk):
                await generations.update(generation.id, progress=progress)

    if paused or await generations.is_cancelled(generation.id):
        return

    values = (await graph.aget_state(config)).values
    owner_id = (
        str(generation.company_id)
        if generation.kind == GenerationKind.INTERVIEW
        else generation.owner_uid
    )
    payload = build_preparation(generation.id, owner_id, generation.text, values)

    if generation.kind == GenerationKind.INTERVIEW:
        set_id: uuid.UUID = await library.create_interview(payload)
    else:
        set_id = await library.create_preparation(payload)

    await generations.update(generation.id, status=Status.DONE, preparation_id=set_id)

    if generation.kind == GenerationKind.INTERVIEW:
        # Companies stores the set and title, so its pages don't have to ask for them.
        await pubsub.publish(
            GENERATION_COMPLETED,
            {
                "generation_id": str(generation.id),
                "company_id": str(generation.company_id),
                "set_id": str(set_id),
                "title": payload.title,
            },
        )
