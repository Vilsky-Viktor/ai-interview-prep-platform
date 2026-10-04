from prepza_common.notifications import NotificationKind, Recipient, notification

from app.constants.sets import OwnerType


def question_notification(question_set, topic: str, kind: NotificationKind) -> dict:
    """For the set's owner: the learner, or every member of the company that owns the interview.
    It names the question's topic, as a question can be long. The library doesn't know which
    interview a set belongs to, so a company gets its list."""
    if question_set.owner_type == OwnerType.COMPANY:
        recipient, link = Recipient.COMPANY, f"/company/{question_set.owner_id}/interviews"
    else:
        recipient, link = Recipient.USER, f"/preparations/{question_set.id}"

    return notification(
        recipient,
        question_set.owner_id,
        kind,
        link,
        title=question_set.title,
        topic=topic,
    )
