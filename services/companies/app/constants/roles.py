from enum import StrEnum


class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    # Sees everything and shares reports, but changes nothing and spends no credits.
    VIEWER = "viewer"


# The roles that change the company, its tests and candidates, and spend its credits.
EDITORS = (Role.OWNER, Role.ADMIN)
