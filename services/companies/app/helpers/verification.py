import re
from urllib.parse import urlsplit

from app.constants.verification import FREE_EMAIL_DOMAINS

DOMAIN = re.compile(r"^(?=.{1,253}$)([a-z0-9-]{1,63}\.)+[a-z]{2,63}$")


def website_domain(website: str) -> str | None:
    """The domain of a website as typed ("https://www.Acme.com/jobs" is "acme.com"), or None
    when it isn't one."""
    text = website.strip().lower()
    host = urlsplit(text if "://" in text else f"https://{text}").hostname or ""
    host = host.removeprefix("www.")

    return host if DOMAIN.match(host) else None


def is_free_domain(domain: str) -> bool:
    return domain in FREE_EMAIL_DOMAINS


def email_on_domain(email: str, domain: str) -> bool:
    """True for an address at the domain or one of its subdomains (ann@eu.acme.com, acme.com)."""
    email_domain = email.rsplit("@", 1)[-1].lower()

    return email_domain == domain or email_domain.endswith(f".{domain}")
