from app.constants.api import CANDIDATE_LINK
from app.schemas.public import Candidate, Interview, Signals


def interview_of(found: dict) -> Interview:
    """Companies' interview, as the API shows it."""
    return Interview(
        id=found["id"],
        title=found["title"],
        status=found["status"],
        ready=found["set_id"] is not None,
        pass_mark=found["pass_mark"],
        candidate_count=found["candidate_count"],
        created_at=found["created_at"],
    )


def candidate_of(found: dict, company_id, interview_id, site: str) -> Candidate:
    """Companies' candidate, as the API shows it, with a link to their results in prepza."""
    return Candidate(
        id=found["id"],
        email=found["email"],
        status=found["status"],
        progress=found["progress"],
        grade=found["grade"],
        passed=found["passed"],
        signals=Signals(
            tab_leaves=found["tab_leaves"],
            copies=found["copies"],
            fast_answers=found["fast_answers"],
        ),
        results_url=CANDIDATE_LINK.format(
            site=site, company_id=company_id, interview_id=interview_id, invite_id=found["id"]
        ),
        created_at=found["created_at"],
    )
