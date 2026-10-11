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
    # Not a person's: a finished candidate's grade changed after an answer key was fixed.
    GRADE_CHANGED = "grade_changed"


# What an audit event was recorded through when not a person in the app (audit_events.via): the
# in-app assistant reading for a member, or an AI app (Claude, ChatGPT, ...) the member connected
# over MCP, which the assistant service serves too. Each is the issuer of the X-Assistant token
# the assistant sends.
VIA_ASSISTANT = "assistant"
VIA_MCP = "mcp"
VIAS = (VIA_ASSISTANT, VIA_MCP)
# Who and what an event made by prepza itself names: the AI that checks answer keys, whose fix
# rescored past answers.
PREPZA = "prepza"
VIA_VERIFIER = "verifier"
