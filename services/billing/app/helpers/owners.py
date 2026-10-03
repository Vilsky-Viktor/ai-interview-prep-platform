from app.constants.products import OwnerType


def owner_of(owner_type: str, owner_id: str) -> dict:
    """Whose wallet a funnel event is about: a learner or a company."""
    if owner_type == OwnerType.COMPANY:
        return {"company_id": owner_id}

    return {"user_id": owner_id}
