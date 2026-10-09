import httpx

from app.constants.show import (
    MAX_ROWS,
    NOTHING_TO_SHOW,
    ONE_EACH,
    PAGE_NAMES,
    PAGES,
    ROW_KINDS,
    SHOWN,
)
from app.helpers.blocks import SAFE_ID, link
from app.integrations import services
from app.models.answers import Turn
from app.services.live_blocks import items_for


async def page_name(page: str, ids: dict, token: str, language: str) -> str | None:
    """What the page is about (an interview's title, a company's name), read with the user's
    token; None for a page named by itself, or when it can't be read."""
    if page not in PAGE_NAMES:
        return None

    path, field = PAGE_NAMES[page]

    try:
        response = await services.get("companies", link(path, ids) or "", {}, token, language)
    except httpx.HTTPError:
        return None

    return response.json().get(field) if response.is_success else None


def row_link(kind: str, ref: dict, company_id: str | None) -> str | None:
    """The page a row opens."""
    page = {"candidate_rows": "candidate", "interview": "interview", "credits": "top_up"}[kind]

    return link(PAGES[page], {"company_id": company_id, **ref})


async def rows_block(arguments: dict, turn: Turn) -> dict | None:
    """The rows the model chose, as the user may see them now (read with their token); None
    when none of them is."""
    kind, keys = ROW_KINDS[arguments["kind"]]
    refs = [
        {key: str(row.get(key, "")) for key in keys}
        for row in (arguments.get("rows") or [])[:MAX_ROWS]
        if all(SAFE_ID.match(str(row.get(key, ""))) for key in keys)
    ]
    # An interview's candidates are read by its id; a candidate's ref uses "id".
    if kind == "candidate_rows":
        refs = [{"id": ref["candidate_id"], "interview_id": ref["interview_id"]} for ref in refs]

    company_id = arguments.get("company_id") or (str(turn.company_id) if turn.company_id else None)
    links = [row_link(kind, {**ref, "candidate_id": ref.get("id")}, company_id) for ref in refs]
    block = {"kind": kind, "refs": refs, "links": links}
    found = await items_for(block, turn.token, turn.language)
    kept = [(item, url) for item, url in zip(found, links, strict=True) if item]

    if not kept:
        return None

    return {
        "kind": kind,
        "items": [item for item, _ in kept],
        "links": [url for _, url in kept],
        "ref": {**block, "refs": [r for r, item in zip(refs, found, strict=True) if item]},
    }


async def link_block(arguments: dict, turn: Turn) -> dict | None:
    """One link to an app page, built from the fixed map and ids (never a URL from the model),
    named by what it opens; None when it can't be built or what it names isn't the user's."""
    page = arguments.get("page")

    if page not in PAGES:
        return None

    ids = {
        key: arguments.get(key)
        for key in ("company_id", "interview_id", "candidate_id", "template_id", "provider")
    }
    ids["company_id"] = ids["company_id"] or (str(turn.company_id) if turn.company_id else None)
    url = link(PAGES[page], ids)

    if url is None:
        return None

    name = await page_name(page, ids, turn.token, turn.language)

    if page in PAGE_NAMES and name is None:
        return None

    ref = {"kind": "link", "page": page, "ids": {k: v for k, v in ids.items() if v}, "links": [url]}

    return {"kind": "link", "items": [], "links": [url], "page": page, "label": name, "ref": ref}


async def show(arguments: dict, turn: Turn, shown: set) -> tuple[dict, dict | None]:
    """What the model reads back, and the block to show (with `ref`, what's kept of it). One
    list and one link an answer: `shown` holds what this answer showed already."""
    kind = arguments.get("kind")
    slot = "link" if kind == "link" else "rows"

    if slot in shown:
        return {"error": 409, "detail": ONE_EACH}, None

    block = await (link_block(arguments, turn) if slot == "link" else rows_block(arguments, turn))

    if block is None:
        return {"error": 404, "detail": NOTHING_TO_SHOW}, None

    shown.add(slot)

    return {"detail": SHOWN}, block


# The reads that are about one interview, or one candidate, by the argument naming it.
INTERVIEW_ARGUMENT = "interview_id"
CANDIDATE_READS = {"get_scorecard": "invite_id"}


async def implied_link(answer, turn: Turn) -> dict | None:
    """The link an answer about one interview or one candidate needs when the model gave none:
    that candidate's report, or that interview's candidates, from what the turn read."""
    interviews, candidates = set(), set()

    for result in answer.results:
        if not result.succeeded:
            continue

        if result.arguments.get(INTERVIEW_ARGUMENT):
            interviews.add(str(result.arguments[INTERVIEW_ARGUMENT]))

        if result.tool in CANDIDATE_READS:
            candidates.add(str(result.arguments.get(CANDIDATE_READS[result.tool])))

    if len(interviews) != 1:
        return None

    [interview_id] = interviews

    if len(candidates) == 1:
        [candidate_id] = candidates
        target = {"page": "candidate", "interview_id": interview_id, "candidate_id": candidate_id}
    else:
        target = {"page": "interview_candidates", "interview_id": interview_id}

    return await link_block({"kind": "link", **target}, turn)


async def finish(answer, turn: Turn, emit) -> None:
    """Sends what the answer shows, once it's written, and keeps its references: the rows, and
    the link to the most specific page (added from what the turn read when the model gave
    none). A single row opens its own page, so it shows alone."""
    rows = next((block for block in answer.shown_blocks if block["kind"] != "link"), None)
    found = next((block for block in answer.shown_blocks if block["kind"] == "link"), None)
    single = rows is not None and len(rows["items"]) == 1

    if single:
        found = None
    elif found is None:
        found = await implied_link(answer, turn)

    for block in (rows, found):
        if block is not None:
            emit({"block": {key: value for key, value in block.items() if key != "ref"}})
            answer.blocks.append(block["ref"])
