from email.message import EmailMessage

from app.templates.emails import (
    CANDIDATE_INVITE_BODY,
    CANDIDATE_INVITE_SUBJECT,
    SHARE_INVITE_BODY,
    SHARE_INVITE_SUBJECT,
)


def share_invite_email(data: dict, site_url: str, sender: str) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = data["email"]
    message["Subject"] = SHARE_INVITE_SUBJECT.format(**data)
    message.set_content(
        SHARE_INVITE_BODY.format(**data, link=f"{site_url.rstrip('/')}/share/{data['token']}")
    )

    return message


def candidate_invite_email(data: dict, site_url: str, sender: str) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = data["email"]
    message["Subject"] = CANDIDATE_INVITE_SUBJECT.format(**data)
    message.set_content(
        CANDIDATE_INVITE_BODY.format(
            **data, link=f"{site_url.rstrip('/')}/invite/{data['token']}"
        )
    )

    return message
