from app.models.audit import AuditEvent
from app.schemas.audit import AuditEventOut


def audit_event_out(row: AuditEvent) -> AuditEventOut:
    return AuditEventOut(
        user_id=row.user_id,
        action=row.action,
        target_id=row.target_id,
        via=row.via,
        created_at=row.created_at,
    )
