from prepza_common.notifications import NotificationKind, Recipient, notification


def question_notification(question_set, topic: str, kind: NotificationKind) -> dict:
    """For every member of the company that owns the interview. It names the question's topic,
    as a question can be long. The library doesn't know which interview a set belongs to, so a
    company gets its list."""
    return notification(
        Recipient.COMPANY,
        question_set.owner_id,
        kind,
        f"/company/{question_set.owner_id}/interviews",
        title=question_set.title,
        topic=topic,
    )
