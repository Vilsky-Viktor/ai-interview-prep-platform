# The events api acts on, from companies.
# A candidate finished an interview: the company's web hooks hear it.
CANDIDATE_FINISHED = "candidate.finished"
# A finished candidate's grade changed (an answer key was corrected): the web hooks hear it again.
CANDIDATE_RESCORED = "candidate.rescored"
# A company was deleted: its keys and web hooks go.
COMPANY_DELETED = "company.deleted"
