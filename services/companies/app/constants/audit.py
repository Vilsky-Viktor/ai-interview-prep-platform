from enum import StrEnum

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
