CANDIDATE_INVITED = "candidate.invited"
# The owner invited a member; notifications emails them the join link.
MEMBER_INVITED = "member.invited"
# A member emails a candidate's PDF report to someone; notifications sends it, attached.
REPORT_SHARED = "report.shared"
# A candidate who hasn't started is reminded once; the event carries what the invite did.
CANDIDATE_REMINDED = "candidate.reminded"
# A company interview's questions are saved; the event carries the set and its title.
GENERATION_COMPLETED = "generation.completed"
# An interview's generation failed; the interview shows it until a retry or its questions.
GENERATION_FAILED = "generation.failed"
# Generation cancelled an interview's topic review that waited too long; the interview goes too.
GENERATION_CANCELLED = "generation.cancelled"
# Rounds: every section of a candidate's interview is finished, with how many answers they
# picked; the company is charged for the candidate, or gets the credits back without one.
INTERVIEW_FINISHED = "interview.finished"
# Rounds: a corrected answer key changed finished candidates' scores; their stored grades follow.
RESULTS_RESCORED = "results.rescored"
# A company was deleted; notifications removes the company's notifications.
COMPANY_DELETED = "company.deleted"
# A candidate's interview.finished was stored: their grade, whether they passed, and the
# interview's title; ats writes the result back to the ATS that sent them.
CANDIDATE_FINISHED = "candidate.finished"
# A finished candidate's stored grade changed (an answer key was corrected since): the same
# result with the new grade and when it was stored; api sends web hooks, ats a new note.
CANDIDATE_RESCORED = "candidate.rescored"
# A generated interview got its questions; ats invites the candidates waiting for it.
INTERVIEW_READY = "interview.ready"
# An interview was deleted; ats removes its job links and the candidates sent for it.
INTERVIEW_DELETED = "interview.deleted"
# Processed events are remembered this long: past Pub/Sub's 7 days of redeliveries.
PROCESSED_EVENT_DAYS = 8
# A company erased a candidate (removed them, results included): other services forget them.
CANDIDATE_REMOVED = "candidate.removed"
