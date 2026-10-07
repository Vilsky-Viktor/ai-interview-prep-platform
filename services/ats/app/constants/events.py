# The events ats acts on, all from companies.
# A candidate finished an interview: their results go back to the ATS that sent them.
CANDIDATE_FINISHED = "candidate.finished"
# An interview's questions are ready: candidates waiting for it are invited.
INTERVIEW_READY = "interview.ready"
# An interview was deleted: its linked jobs and candidates go.
INTERVIEW_DELETED = "interview.deleted"
# A company was deleted: its connections go, with their linked jobs and candidates.
COMPANY_DELETED = "company.deleted"
