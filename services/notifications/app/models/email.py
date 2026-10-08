from dataclasses import dataclass, field


@dataclass
class Email:
    to: str
    subject: str
    html: str
    text: str
    # Sent with the email; Resend's webhooks carry them back.
    tags: dict[str, str] = field(default_factory=dict)
    # Where a reply goes, when not to the sender: the visitor who wrote through the contact page.
    reply_to: str | None = None
    # Extra headers: the one-click unsubscribe of optional emails and candidate reminders.
    headers: dict[str, str] = field(default_factory=dict)
    # Files sent with it: (file name, base64 content).
    attachments: list[tuple[str, str]] = field(default_factory=list)
