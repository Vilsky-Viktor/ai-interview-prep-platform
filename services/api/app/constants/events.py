# The events api acts on, from companies.
# A candidate finished an interview: the company's web hooks hear it.
CANDIDATE_FINISHED = "candidate.finished"
# A company erased a candidate: their results waiting to be sent again to its web hooks go.
CANDIDATE_REMOVED = "candidate.removed"
# A company was deleted: its keys and web hooks go.
COMPANY_DELETED = "company.deleted"
