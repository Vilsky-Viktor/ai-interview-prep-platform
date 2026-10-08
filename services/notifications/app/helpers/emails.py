from html import escape

from prepza_common.constants import DEFAULT_LANGUAGE, RTL_LANGUAGES

from app.constants.unsubscribe import SETTINGS_PATH, UnsubscribeType
from app.constants.webhooks import CANDIDATE_INVITE_KIND, ID_TAG, KIND_TAG
from app.helpers.unsubscribe import candidate_token, one_click_headers, page_url, user_token
from app.models.email import Email
from app.templates.contact import CONTACT_HTML, CONTACT_SUBJECT, CONTACT_TEXT
from app.templates.emails import EMAILS
from app.templates.layout import (
    HTML_FOOTER_LINK,
    HTML_LAYOUT,
    HTML_LOGO,
    HTML_NAME,
    HTML_PARAGRAPH,
    HTML_ROW,
    HTML_SECTION,
    HTML_SECTION_HEADING,
    PREHEADER_PADDING,
    TEXT_FOOTER_LINK,
    TEXT_LAYOUT,
    TEXT_ROW,
    TEXT_SECTION_HEADING,
)

# A list under an email's text: its heading ("" for none) and its items, each the key of its
# line in the template's "rows", the values that fill it, and where it links.
Section = tuple[str, list[tuple[str, dict, str]]]


def render(
    kind: str,
    data: dict,
    link: str,
    links: list[tuple[str, str]] = (),
    sections: list[Section] = (),
) -> Email:
    """Builds the plain-text and HTML versions of the `kind` email ("candidate"), in the
    interview's language (English for older events), right to left where that language is;
    names and titles are escaped in the HTML. `sections` are lists after the text. `links` go
    under the footer: each one's text (a key of the language's texts) and address."""
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

    footer_links = [(texts[key], url) for key, url in links]
    # Each list's heading and its lines, filled in.
    filled = [
        (heading, [(template["rows"][row].format(**values), url) for row, values, url in rows])
        for heading, rows in sections
    ]

    text = TEXT_LAYOUT.format(
        heading=template["heading"],
        lines="\n\n".join(line.format(**data) for line in template["lines"]),
        sections="".join(
            "\n"
            + (TEXT_SECTION_HEADING.format(heading=heading) if heading else "")
            + "".join(TEXT_ROW.format(text=text, url=url) for text, url in rows)
            for heading, rows in filled
        ),
        button=template["button"],
        link=link,
        footer=footer.format(**data),
        links="\n"
        + "".join(
            TEXT_FOOTER_LINK.format(text=label.format(**data), url=url)
            for label, url in footer_links
        )
        if footer_links
        else "",
    )
    html = HTML_LAYOUT.format(
        subject=escape(template["subject"].format(**data)),
        preheader=template["preheader"].format(**safe),
        padding=PREHEADER_PADDING,
        heading=template["heading"],
        lines="\n".join(
            HTML_PARAGRAPH.format(text=line.format(**emphasized)) for line in template["lines"]
        ),
        sections="".join(
            HTML_SECTION.format(
                heading=HTML_SECTION_HEADING.format(heading=escape(heading)) if heading else "",
                rows="".join(
                    HTML_ROW.format(text=escape(text), url=escape(url)) for text, url in rows
                ),
            )
            for heading, rows in filled
        ),
        button=template["button"],
        link=escape(link),
        footer=footer.format(**safe),
        links="<br>"
        + "".join(
            HTML_FOOTER_LINK.format(text=label.format(**safe), url=escape(url))
            for label, url in footer_links
        )
        if footer_links
        else "",
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


def candidate_invite_email(data: dict, site_url: str, secret: str) -> Email:
    """The invite, with a link that stops the company's emails to this address (events saved
    before invites carried the company's id have none)."""
    data = with_logo(data, site_url)
    links = (
        [
            (
                "stop_company",
                page_url(site_url, candidate_token(data, UnsubscribeType.COMPANY, secret)),
            )
        ]
        if data.get("company_id")
        else []
    )
    email = render("candidate", data, f"{site_url.rstrip('/')}/invite/{data['token']}", links)
    email.tags = invite_tags(CANDIDATE_INVITE_KIND, data.get("invite_id"))

    return email


def candidate_reminder_email(data: dict, site_url: str, secret: str) -> Email:
    """The one reminder to a candidate who hasn't started: the same invite link. Tagged like the
    invite, so a bounce marks the invite undelivered. Its links stop this invite's reminders or
    all the company's emails; a mail client's own unsubscribe stops the reminders."""
    data = with_logo(data, site_url)
    links = []
    headers = {}

    if data.get("company_id") and data.get("invite_id"):
        reminders = candidate_token(data, UnsubscribeType.INVITE_REMINDERS, secret)
        company = candidate_token(data, UnsubscribeType.COMPANY, secret)
        links = [
            ("stop_reminders", page_url(site_url, reminders)),
            ("stop_company", page_url(site_url, company)),
        ]
        headers = one_click_headers(site_url, reminders)

    email = render("reminder", data, f"{site_url.rstrip('/')}/invite/{data['token']}", links)
    email.tags = invite_tags(CANDIDATE_INVITE_KIND, data.get("invite_id"))
    email.headers.update(headers)

    return email


def optional_email(
    kind: str,
    data: dict,
    link: str,
    site_url: str,
    secret: str,
    user_id: str,
    unsubscribe: UnsubscribeType,
    sections: list[Section] = (),
) -> Email:
    """An email a prepza user may turn off (the activity digest, reminders, updates, offers):
    the `kind` email, with "Unsubscribe" (from `unsubscribe`) and "Change your email settings"
    under its footer, and the one-click unsubscribe headers mail clients show as a button. Sent
    from the optional emails' own address, and tagged with the user and `unsubscribe`, so a spam
    complaint about it turns it off (services/webhooks.py)."""
    token = user_token(user_id, unsubscribe, secret)
    links = [
        ("unsubscribe", page_url(site_url, token)),
        ("email_settings", site_url.rstrip("/") + SETTINGS_PATH),
    ]
    email = render(kind, data, link, links, sections)
    email.headers.update(one_click_headers(site_url, token))
    email.optional = True
    email.tags = {KIND_TAG: unsubscribe, ID_TAG: user_id}

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
