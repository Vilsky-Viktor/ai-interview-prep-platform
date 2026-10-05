from app.constants.logos import LOGO_PATH, LOGO_SIGNATURES, MAX_LOGO_BYTES, WEBP_TYPE
from app.models.companies import Company


def logo_type(content: bytes) -> str | None:
    """The media type of a PNG, JPEG or WebP image no larger than MAX_LOGO_BYTES; None for
    anything else."""
    if not content or len(content) > MAX_LOGO_BYTES:
        return None

    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return WEBP_TYPE

    return next(
        (kind for signature, kind in LOGO_SIGNATURES if content.startswith(signature)), None
    )


def logo_path(company: Company | None) -> str | None:
    """The logo's address on the site, or None when the company has none."""
    if company is None or company.logo_type is None:
        return None

    return LOGO_PATH.format(company_id=company.id, version=company.logo_version)
