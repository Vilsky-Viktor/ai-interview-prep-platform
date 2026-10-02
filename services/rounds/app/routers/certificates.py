from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.certificates import CertificateOut
from app.storage import certificates

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("/{certificate_id}")
async def get_certificate(certificate_id: UUID) -> CertificateOut:
    """Public, no auth: certificates are shared by link."""
    certificate = await certificates.get(certificate_id)

    if certificate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificate not found")

    return CertificateOut(
        id=certificate.id,
        user_name=certificate.user_name,
        topic_title=certificate.topic_title,
        score=certificate.score,
        issued_at=certificate.issued_at,
        preparation_id=certificate.preparation_id,
    )
