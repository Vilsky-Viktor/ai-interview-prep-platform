from enum import StrEnum


class InviteStatus(StrEnum):
    INVITED = "invited"
    IN_PROCESS = "in_process"
    FINISHED = "finished"
