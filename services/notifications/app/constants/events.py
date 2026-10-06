# A service asks for an in-app notification (prepza_common.notifications).
from prepza_common.notifications import NOTIFICATION_REQUESTED  # noqa: F401 (re-exported)

CANDIDATE_INVITED = "candidate.invited"
# A candidate who hasn't started, reminded once; the same data as the invite.
CANDIDATE_REMINDED = "candidate.reminded"
# A company member emails a candidate's PDF report; it carries the PDF, base64-encoded.
REPORT_SHARED = "report.shared"
# A visitor wrote through the contact page; it's emailed to prepza's inbox.
CONTACT_SENT = "contact.sent"
# Companies: a company was deleted; its notifications go with it.
COMPANY_DELETED = "company.deleted"
