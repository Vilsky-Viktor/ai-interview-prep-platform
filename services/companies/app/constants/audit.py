from enum import StrEnum

from prepza_common.constants import VIA_ASSISTANT, VIA_MCP

# Audit events are kept this long (24 months), then the daily retention deletes them.
AUDIT_RETENTION_DAYS = 730


class AuditAction(StrEnum):
    """The human decisions recorded as evidence of oversight."""

    TOPICS_APPROVED = "topics_approved"
    RESULTS_VIEWED = "results_viewed"
    REPORT_EMAILED = "report_emailed"
    CANDIDATE_DELETED = "candidate_deleted"
    INVITE_REVOKED = "invite_revoked"
    EXTRA_TIME_SET = "extra_time_set"
    PASS_MARK_CHANGED = "pass_mark_changed"
    # Who answers for the company changed hands.
    OWNERSHIP_TRANSFERRED = "ownership_transferred"
    # Whether AI apps members connected may use the company's data.
    AI_APPS_CHANGED = "ai_apps_changed"


# What an audit event can be recorded through when not a person in the app (audit_events.via).
VIAS = (VIA_ASSISTANT, VIA_MCP)
# A change made with an API key, recorded as the owner or admin who made it.
VIA_API = "api"
