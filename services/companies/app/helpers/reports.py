import base64
import binascii

from app.constants.reports import MAX_REPORT_BYTES, PDF_SIGNATURE


def is_report_pdf(pdf: str) -> bool:
    """True when the base64 text is a PDF no larger than MAX_REPORT_BYTES."""
    try:
        content = base64.b64decode(pdf, validate=True)
    except binascii.Error:
        return False

    return len(content) <= MAX_REPORT_BYTES and content.startswith(PDF_SIGNATURE)
