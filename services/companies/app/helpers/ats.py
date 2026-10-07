import re
from html.parser import HTMLParser

from app.constants.ats import WORKABLE_SUBDOMAIN


def workable_subdomain(text: str) -> str | None:
    """The account's subdomain from what a company pasted: "acme", "acme.workable.com" or its
    full address; None when it isn't one."""
    value = text.strip().lower().removeprefix("https://").removeprefix("http://")
    value = value.split("/")[0].removesuffix(".workable.com")

    return value if re.fullmatch(WORKABLE_SUBDOMAIN, value) else None


# Tags that start a new line in plain text, and list items, which get a dash.
BLOCK_TAGS = {"p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "tr"}


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

        if tag == "li":
            self.parts.append("\n- ")

    def handle_endtag(self, tag: str) -> None:
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def html_to_text(html: str) -> str:
    """An ATS's HTML job text as plain text: paragraphs and list items on their own lines, at
    most one empty line between them."""
    parser = _Text()
    parser.feed(html or "")
    lines = [" ".join(line.split()) for line in "".join(parser.parts).splitlines()]
    text = "\n".join(lines)

    return re.sub(r"\n{3,}", "\n\n", text).strip()


def job_text(title: str, sections: list[str], limit: int) -> str:
    """A job as one plain text to make an interview from: its title, then each non-empty HTML
    section (description, requirements…), cut to `limit` characters."""
    parts = [title.strip(), *(html_to_text(section) for section in sections)]

    return "\n\n".join(part for part in parts if part)[:limit]
