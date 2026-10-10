from enum import StrEnum


class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    # Sees everything and shares reports, but changes nothing and spends no credits.
    VIEWER = "viewer"


# The roles that change the company, its tests and candidates, and spend its credits.
EDITORS = (Role.OWNER, Role.ADMIN)

# Team invites email whoever the owner names, from prepza's domain: a company holds at most this
# many not yet accepted, and one that never topped up sends at most this many a day.
MAX_PENDING_INVITES = 20
MEMBER_INVITES_PER_UNPAID_DAY = 10
TOO_MANY_PENDING = "Too many invites waiting. Remove some, or wait for them to join."
