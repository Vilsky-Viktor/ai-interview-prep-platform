from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from prepza_common.constants import (
    MAX_CAMPAIGN_BUTTON_LENGTH,
    MAX_CAMPAIGN_SUBJECT_LENGTH,
    MAX_CAMPAIGN_TEXT_LENGTH,
)
from prepza_common.user import Language
from pydantic import BaseModel, StringConstraints

Subject = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_CAMPAIGN_SUBJECT_LENGTH),
]
Text = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_CAMPAIGN_TEXT_LENGTH)
]
ButtonText = Annotated[
    str, StringConstraints(strip_whitespace=True, max_length=MAX_CAMPAIGN_BUTTON_LENGTH)
]
CampaignKind = Literal["updates", "promotions"]


class CampaignTexts(BaseModel):
    """A campaign in one language: its subject (also the email's heading), its text (in Markdown:
    the editor's bold, italic, links and lists) and its button's text."""

    subject: Subject
    text: Text
    button: ButtonText | None = None


class CampaignIn(CampaignTexts):
    """A campaign as a superadmin writes it, in English: a product update or an offer, and the
    page on the site its button opens."""

    kind: CampaignKind
    link: Annotated[str, StringConstraints(strip_whitespace=True, max_length=300)] | None = None


class CampaignCounts(BaseModel):
    pending: int
    sent: int
    skipped: int
    failed: int
    # Turned the campaign's setting off from it, or marked it as spam (complained).
    unsubscribed: int
    complained: int


class CampaignRowOut(BaseModel):
    """A campaign in the list: its English subject, whether every language has its texts, where
    it stands (a draft, being sent, sent to everyone, or stopped) and once it's sent, its
    counts."""

    id: UUID
    kind: CampaignKind
    subject: str
    created_at: datetime
    sent_at: datetime | None
    translated: bool
    status: Literal["draft", "sending", "sent", "stopped"]
    counts: CampaignCounts | None


class CampaignOut(CampaignRowOut):
    link: str | None
    # By language; a language without texts gets the English.
    texts: dict[str, CampaignTexts]


class RecipientsOut(BaseModel):
    """Who the campaign would reach now: users with its setting on, not suppressed, with an
    address."""

    count: int


class PreviewOut(BaseModel):
    subject: str
    html: str


class CampaignSourceOut(BaseModel):
    """A campaign to translate (generation): its English texts and the languages it lacks."""

    subject: str
    text: str
    button: str | None
    missing: list[str]


class CampaignTranslationsIn(BaseModel):
    """Translations of the campaign's English texts (subject, text, button): saved only while it
    still reads so and isn't sent."""

    subject: str
    text: str
    button: str | None
    translations: dict[Language, CampaignTexts]
