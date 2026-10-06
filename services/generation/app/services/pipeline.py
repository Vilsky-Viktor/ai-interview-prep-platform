import uuid
from contextlib import aclosing

from langgraph.types import Command

from app.constants.events import GENERATION_COMPLETED
from app.constants.generation import MAX_CONCURRENCY, RECURSION_LIMIT
from app.constants.kinds import GenerationKind
from app.constants.statuses import Status
from app.helpers.payload import build_preparation
from app.helpers.progress import track_progress
from app.helpers.questions import topic_size
from app.integrations import library
from app.models.generation import Generation
from app.services import outbox as outbox_service
from app.services.sample_checks import check_sample
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
        graph_input = {
            "input_text": generation.text,
            "language": generation.language,
            "template": generation.kind == GenerationKind.TEMPLATE,
        }

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

            if track_progress(
                progress, chunk, topic_size(generation.kind == GenerationKind.TEMPLATE)
            ):
                await generations.update(generation.id, progress=progress)

    if paused or await generations.is_cancelled(generation.id):
        return

    values = (await graph.aget_state(config)).values

    if generation.kind == GenerationKind.TEMPLATE:
        payload = build_preparation(generation.id, generation.owner_uid, generation.text, values)
        set_id = await library.create_template(payload)
        await check_sample(set_id)
        await finish(generation.id, set_id)

        return

    payload = build_preparation(generation.id, str(generation.company_id), generation.text, values)
    set_id: uuid.UUID = await library.create_interview(payload)
    # Checked before companies hears it's ready, so no candidate sees an unchecked key.
    await check_sample(set_id)
    # Companies stores the test's set and title, so its pages don't have to ask for them.
    completed = (
        GENERATION_COMPLETED,
        {
            "generation_id": str(generation.id),
            "company_id": str(generation.company_id),
            "set_id": str(set_id),
            "title": payload.title,
        },
    )
    await finish(generation.id, set_id, completed)
    await outbox_service.flush_quietly()


async def finish(generation_id: uuid.UUID, set_id: uuid.UUID, event=None) -> None:
    """Marks the generation done with its saved set. Cancelled while the set was being saved,
    it stays cancelled, and the set nobody will use is deleted."""
    if not await generations.update(
        generation_id, event=event, status=Status.DONE, preparation_id=set_id
    ):
        await library.delete_set(set_id)
