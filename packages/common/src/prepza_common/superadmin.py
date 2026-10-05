# Superadmins: prepza's own team, not a company's admins. They manage templates and the question
# bank, and are the verified Google accounts listed in SUPERADMIN_EMAILS, comma-separated. Every
# service reads the same setting.
import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from prepza_common.auth import current_user
from prepza_common.user import User


def is_superadmin(user: User) -> bool:
    emails = {email.strip().lower() for email in os.environ.get("SUPERADMIN_EMAILS", "").split(",")}

    return user.email_verified and user.email.lower() in emails - {""}


def superadmin_user(user: Annotated[User, Depends(current_user)]) -> User:
    """Not found for everyone else, so superadmin routes don't show they exist."""
    if not is_superadmin(user):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")

    return user


SuperadminUser = Annotated[User, Depends(superadmin_user)]
