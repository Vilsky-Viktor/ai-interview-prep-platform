from enum import StrEnum


class InviteStatus(StrEnum):
    INVITED = "invited"
    IN_PROCESS = "in_process"
    FINISHED = "finished"
    # The candidate deleted their account: their email and results are gone.
    DELETED = "deleted"


# Candidate invites, with the candidate's results, are kept this long after they're sent.
CANDIDATE_RETENTION_DAYS = 365
