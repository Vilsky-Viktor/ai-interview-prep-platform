"""Candidates in a pasted or uploaded list: their emails, and their names where the list gives
them, as "Name <email>" or "email, Name" lines, or a CSV with name columns in its header."""

import csv
import re

from prepza_common.names import clean_name

from app.constants.invites import EMAIL_PATTERN
from app.constants.name_headers import (
    FIRST_NAME_HEADERS,
    FULL_NAME_HEADERS,
    LAST_NAME_HEADERS,
)
from app.helpers.email_lists import emails_in

NAME_THEN_EMAIL = re.compile(rf'^\s*"?(?P<name>[^<>"@]*?)"?\s*<(?P<email>{EMAIL_PATTERN})>[\s,;]*$')
EMAIL_THEN_NAME = re.compile(
    rf'^\s*<?(?P<email>{EMAIL_PATTERN})>?\s*[,;\t]\s*"?(?P<name>[^,;\t"<>@]+?)"?[\s,;]*$'
)
DELIMITERS = ",;\t"


def candidates_in(text: str) -> list[tuple[str, str | None]]:
    """Each email in the text once, lowercased, in the order it first appears, with the first
    name given for it (None without one). Other text around the emails is ignored."""
    lines = [line for line in text.splitlines() if line.strip()]
    names = (csv_names(lines) if lines else None) or line_names(lines)
    found: dict[str, str | None] = {}

    for email in emails_in(text):
        found.setdefault(email, names.get(email))

    return list(found.items())


def line_names(lines: list[str]) -> dict[str, str]:
    """Names of "Name <email>" and "email, Name" lines, by email."""
    names = {}

    for line in lines:
        match = NAME_THEN_EMAIL.match(line) or EMAIL_THEN_NAME.match(line)
        name = clean_name(match["name"]) if match else None

        if name:
            names.setdefault(match["email"].lower().strip("."), name)

    return names


def header_key(cell: str) -> str:
    return " ".join(re.sub(r"[_\-]", " ", cell.strip().strip('"').lower()).split())


def csv_names(lines: list[str]) -> dict[str, str] | None:
    """Names from a CSV whose first line is a header with a name column (a whole name, or a
    first name with a last name), by email; None when the first line isn't such a header."""
    delimiter = max(DELIMITERS, key=lines[0].count)
    header = [header_key(cell) for cell in next(csv.reader([lines[0]], delimiter=delimiter))]
    first = next((i for i, cell in enumerate(header) if cell in FIRST_NAME_HEADERS), None)
    last = next((i for i, cell in enumerate(header) if cell in LAST_NAME_HEADERS), None)
    full = next((i for i, cell in enumerate(header) if cell in FULL_NAME_HEADERS), None)

    # "Имя, Фамилия": beside a last name, a name column holds the first name.
    if first is None and last not in (None, full):
        first = full

    columns = [first, last] if first is not None else [full]
    columns = [column for column in columns if column is not None]

    if not columns:
        return None

    names = {}

    for row in csv.reader(lines[1:], delimiter=delimiter):
        emails = emails_in(delimiter.join(row))
        parts = [row[column] for column in columns if column < len(row)]
        name = clean_name(" ".join(part.strip() for part in parts))

        if emails and name:
            names.setdefault(emails[0], name)

    return names
