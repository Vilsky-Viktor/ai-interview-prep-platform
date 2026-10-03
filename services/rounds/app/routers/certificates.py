from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from prepza_common.auth import CurrentUser
from prepza_common.i18n import request_language

from app.constants.rounds import CERTIFICATE_RULES
from app.models.certificates import Certificate
from app.schemas.certificates import CertificateOut
from app.services.certificate_purchase import buy_certificate
from app.storage import certificates

router = APIRouter(prefix="/certificates", tags=["certificates"])


def certificate_out(certificate: Certificate) -> CertificateOut:
    return CertificateOut(
        id=certificate.id,
        user_name=certificate.user_name,
        topic_title=certificate.topic_title,
        score=certificate.score,
        issued_at=certificate.issued_at,
        preparation_id=certificate.preparation_id,
    )


@router.get("/rules")
async def get_rules(request: Request) -> list[str]:
    """What earns a topic's certificate; public, shown before practicing. Declared before
    /{certificate_id}, which would otherwise take "rules" as an id."""
    return CERTIFICATE_RULES[request_language(request)]


@router.post("/topics/{topic_id}", status_code=status.HTTP_201_CREATED)
async def buy(topic_id: UUID, user: CurrentUser) -> CertificateOut:
    """Charges and issues an earned certificate on someone else's public kit."""
    return certificate_out(await buy_certificate(topic_id, user))


@router.get("/{certificate_id}")
async def get_certificate(certificate_id: UUID) -> CertificateOut:
    """Public, no auth: certificates are shared by link."""
    certificate = await certificates.get(certificate_id)

    if certificate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificate not found")

    return certificate_out(certificate)
