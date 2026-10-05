from itertools import groupby

from app.constants.talents import MAX_SUGGESTED, MIN_SUGGESTED_GRADE
from app.helpers.practice import round_grade
from app.schemas.talents import SuggestedTalent


def suggestions(rows: list, links: dict, template_ids: list) -> list[SuggestedTalent]:
    """Each talent's first round on each template counts, once finished: later rounds repeat
    questions whose answers were shown. A talent is suggested with their best such grade (the
    closer template first on a tie) when it's at least MIN_SUGGESTED_GRADE; best first."""
    order = {template_id: index for index, template_id in enumerate(template_ids)}
    best = {}
    key = lambda row: (row.user_id, row.interview_set_id)

    for (user_id, template_id), sections in groupby(sorted(rows, key=key), key=key):
        sections = list(sections)
        first = min(row.started_at for row in sections)
        first_round = sections[
            next(i for i, row in enumerate(sections) if row.started_at == first)
        ].candidate_invite_id
        finished, grade = round_grade(
            [row for row in sections if row.candidate_invite_id == first_round]
        )

        if not finished or grade < MIN_SUGGESTED_GRADE:
            continue

        current = best.get(user_id)

        if current is None or (grade, -order[template_id]) > (
            current.grade,
            -order[current.template_id],
        ):
            best[user_id] = SuggestedTalent(
                name=links[user_id].name,
                url=links[user_id].url,
                grade=grade,
                template_id=template_id,
            )

    return sorted(best.values(), key=lambda talent: -talent.grade)[:MAX_SUGGESTED]
