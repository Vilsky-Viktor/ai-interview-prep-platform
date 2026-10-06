import logging
from datetime import UTC, datetime, timedelta

from app.constants.audit import AUDIT_RETENTION_DAYS
from app.constants.invites import CANDIDATE_RETENTION_DAYS
from app.integrations import rounds
from app.storage import accounts, audit

logger = logging.getLogger(__name__)


async def delete_expired_candidates() -> int:
    """Candidate invites older than CANDIDATE_RETENTION_DAYS go, with the candidates' answers,
    timings and page-leave signals in rounds. Rounds first, so a failure is retried whole."""
    before = datetime.now(UTC) - timedelta(days=CANDIDATE_RETENTION_DAYS)
    invite_ids = await accounts.expired_invites(before)

    if invite_ids:
        await rounds.delete_invite_sessions(invite_ids)
        await accounts.delete_invites(invite_ids)

    return len(invite_ids)


async def delete_old_audit_events() -> int:
    """Audit events older than AUDIT_RETENTION_DAYS go."""
    before = datetime.now(UTC) - timedelta(days=AUDIT_RETENTION_DAYS)

    return await audit.delete_before(before)
