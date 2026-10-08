# Resend's webhook events meaning the email never reached the inbox: a permanent bounce, a spam
# complaint, or an address Resend won't send to after an earlier one.
COMPLAINED_EVENT = "email.complained"
UNDELIVERED_EVENTS = {"email.bounced", COMPLAINED_EVENT, "email.suppressed"}

# Resend signs each webhook with a timestamp; older ones are refused, so a captured one can't
# be replayed.
WEBHOOK_TOLERANCE_SECONDS = 5 * 60

# Tags Resend's webhooks carry back: what the email is and its id. A candidate's invite and
# reminder: "candidate_invite" and the invite's id; an optional email: its unsubscribe type
# ("digest", "reminders") and the user's id.
KIND_TAG = "kind"
ID_TAG = "id"
CANDIDATE_INVITE_KIND = "candidate_invite"
