# A service asks for an in-app notification (prepza_common.notifications).
from prepza_common.notifications import NOTIFICATION_REQUESTED  # noqa: F401 (re-exported)

PREPARATION_SHARED = "preparation.shared"
CANDIDATE_INVITED = "candidate.invited"
# A visitor wrote through the contact page; it's emailed to prepza's inbox.
CONTACT_SENT = "contact.sent"
