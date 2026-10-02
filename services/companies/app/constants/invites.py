from enum import StrEnum


class InviteStatus(StrEnum):
    INVITED = "invited"
    IN_PROCESS = "in_process"
    FINISHED = "finished"
    # The candidate deleted their account: their email and results are gone.
    DELETED = "deleted"


# Candidate invites, with the candidate's results, are kept this long after they're sent.
CANDIDATE_RETENTION_DAYS = 365
# How often retention runs; deleting is safe to repeat, so every replica may run it.
RETENTION_INTERVAL_SECONDS = 24 * 60 * 60
