from app.helpers.audit import audit_event_out
from app.models.audit import AuditEvent
from app.schemas.audit import ActionOut
from app.storage import action_names


async def rows(company_id, events: list[AuditEvent]) -> list[ActionOut]:
    """The log's rows, each with who took it and what it was about, found in one query each."""
    emails = await action_names.member_emails(company_id, [event.user_id for event in events])
    targets = await action_names.target_names(
        company_id, [event.target_id for event in events if event.target_id]
    )

    return [
        ActionOut(
            **audit_event_out(event).model_dump(),
            id=event.id,
            group=event.group,
            user_email=emails.get(event.user_id),
            target_kind=event.target_kind,
            target=targets.get(event.target_id) or event.target_label,
            removed=event.removed,
        )
        for event in events
    ]
