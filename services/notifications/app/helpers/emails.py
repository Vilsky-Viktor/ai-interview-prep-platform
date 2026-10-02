from html import escape

from app.constants.webhooks import CANDIDATE_INVITE_KIND, ID_TAG, KIND_TAG, SHARE_KIND
from app.models.email import Email
from app.templates.emails import CANDIDATE_INVITE, FOOTER, SHARE_INVITE
from app.templates.layout import (
    HTML_LAYOUT,
    HTML_NAME,
    HTML_PARAGRAPH,
    PREHEADER_PADDING,
    TEXT_LAYOUT,
)


def render(template: dict, data: dict, link: str) -> Email:
    """Builds the plain-text and HTML versions; names and titles are escaped in the HTML."""
    safe = {key: escape(str(value)) for key, value in data.items()}
    emphasized = {
        **safe,
        **{key: HTML_NAME.format(name=safe[key]) for key in ("company", "inviter") if key in safe},
    }

    text = TEXT_LAYOUT.format(
        heading=template["heading"],
        lines="\n\n".join(line.format(**data) for line in template["lines"]),
        button=template["button"],
        link=link,
        footer=FOOTER.format(**data),
    )
    html = HTML_LAYOUT.format(
        subject=escape(template["subject"].format(**data)),
        preheader=template["preheader"].format(**safe),
        padding=PREHEADER_PADDING,
        heading=template["heading"],
        lines="\n".join(
            HTML_PARAGRAPH.format(text=line.format(**emphasized)) for line in template["lines"]
        ),
        button=template["button"],
        link=escape(link),
        footer=FOOTER.format(**safe),
    )

    return Email(to=data["email"], subject=template["subject"].format(**data), html=html, text=text)


def invite_tags(kind: str, invite_id: str | None) -> dict[str, str]:
    """Events saved before invites carried their id get no tags."""
    if invite_id is None:
        return {}

    return {KIND_TAG: kind, ID_TAG: invite_id}


def share_invite_email(data: dict, site_url: str) -> Email:
    email = render(SHARE_INVITE, data, f"{site_url.rstrip('/')}/share/{data['token']}")
    email.tags = invite_tags(SHARE_KIND, data.get("share_id"))

    return email


def candidate_invite_email(data: dict, site_url: str) -> Email:
    email = render(CANDIDATE_INVITE, data, f"{site_url.rstrip('/')}/invite/{data['token']}")
    email.tags = invite_tags(CANDIDATE_INVITE_KIND, data.get("invite_id"))

    return email
