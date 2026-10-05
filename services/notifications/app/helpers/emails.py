from html import escape

from prepza_common.constants import DEFAULT_LANGUAGE, RTL_LANGUAGES

from app.constants.webhooks import CANDIDATE_INVITE_KIND, ID_TAG, KIND_TAG
from app.models.email import Email
from app.templates.contact import CONTACT_HTML, CONTACT_SUBJECT, CONTACT_TEXT
from app.templates.emails import EMAILS
from app.templates.layout import (
    HTML_LAYOUT,
    HTML_LOGO,
    HTML_NAME,
    HTML_PARAGRAPH,
    PREHEADER_PADDING,
    TEXT_LAYOUT,
)


def render(kind: str, data: dict, link: str) -> Email:
    """Builds the plain-text and HTML versions of the `kind` email ("candidate"), in the
    interview's language (English for older events), right to left where that language is;
    names and titles are escaped in the HTML."""
    language = data.get("language")
    # English until the language has this email (new emails are translated later).
    language = language if kind in EMAILS.get(language, {}) else DEFAULT_LANGUAGE
    texts = EMAILS[language]
    template = texts[kind]
    # An email with its own reason for being sent says so; the others share the general one.
    footer = template.get("footer", texts["footer"])
    rtl = language in RTL_LANGUAGES
    safe = {key: escape(str(value)) for key, value in data.items()}
    emphasized = {
        **safe,
        **{
            key: HTML_NAME.format(name=safe[key])
            for key in ("company", "inviter", "sender")
            if key in safe
        },
    }

    text = TEXT_LAYOUT.format(
        heading=template["heading"],
        lines="\n\n".join(line.format(**data) for line in template["lines"]),
        button=template["button"],
        link=link,
        footer=footer.format(**data),
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
        footer=footer.format(**safe),
        language=language,
        direction="rtl" if rtl else "ltr",
        align="right" if rtl else "left",
        paste_link=texts["paste_link"],
        logo=HTML_LOGO.format(url=escape(data["logo_url"]), alt=safe.get("company", ""))
        if data.get("logo_url")
        else "",
    )

    return Email(to=data["email"], subject=template["subject"].format(**data), html=html, text=text)


def invite_tags(kind: str, invite_id: str | None) -> dict[str, str]:
    """Events saved before invites carried their id get no tags."""
    if invite_id is None:
        return {}

    return {KIND_TAG: kind, ID_TAG: invite_id}


def with_logo(data: dict, site_url: str) -> dict:
    """The invite's data with the company logo's full address, when the company has a logo."""
    path = data.get("logo_path")

    return {**data, "logo_url": f"{site_url.rstrip('/')}{path}"} if path else data


def candidate_invite_email(data: dict, site_url: str) -> Email:
    data = with_logo(data, site_url)
    email = render("candidate", data, f"{site_url.rstrip('/')}/invite/{data['token']}")
    email.tags = invite_tags(CANDIDATE_INVITE_KIND, data.get("invite_id"))

    return email


def candidate_reminder_email(data: dict, site_url: str) -> Email:
    """The one reminder to a candidate who hasn't started: the same invite link. Tagged like the
    invite, so a bounce marks the invite undelivered."""
    data = with_logo(data, site_url)
    email = render("reminder", data, f"{site_url.rstrip('/')}/invite/{data['token']}")
    email.tags = invite_tags(CANDIDATE_INVITE_KIND, data.get("invite_id"))

    return email


def report_email(data: dict, site_url: str) -> Email:
    """A PDF report, from a company member to someone such as a hiring manager: a candidate's,
    or all of a test's candidates' ("kind": "candidates"); replying answers the member."""
    texts = {key: value for key, value in data.items() if key not in ("pdf", "kind")}
    email = render(data.get("kind", "report"), texts, site_url)
    email.reply_to = data["reply_to"]
    email.attachments = [(data["filename"], data["pdf"])]

    return email


def contact_email(data: dict, inbox: str) -> Email:
    """The contact page's message, to prepza's inbox; replying answers the visitor."""
    safe = {key: escape(str(value)) for key, value in data.items()}

    return Email(
        to=inbox,
        # One line, whatever the visitor typed as their name.
        subject=CONTACT_SUBJECT.format(name=" ".join(data["name"].split())),
        html=CONTACT_HTML.format(**safe),
        text=CONTACT_TEXT.format(**data),
        reply_to=data["email"],
    )
