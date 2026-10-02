from dataclasses import dataclass, field


@dataclass
class Email:
    to: str
    subject: str
    html: str
    text: str
    # Sent with the email; Resend's webhooks carry them back.
    tags: dict[str, str] = field(default_factory=dict)
