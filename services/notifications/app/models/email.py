from dataclasses import dataclass


@dataclass
class Email:
    to: str
    subject: str
    html: str
    text: str
