# Resend's webhook events meaning the email never reached the inbox: a permanent bounce, a spam
# complaint, or an address Resend won't send to after an earlier one.
UNDELIVERED_EVENTS = {"email.bounced", "email.complained", "email.suppressed"}

# Resend signs each webhook with a timestamp; older ones are refused, so a captured one can't
# be replayed.
WEBHOOK_TOLERANCE_SECONDS = 5 * 60

# Tags on every invite email, which Resend's webhooks carry back: what it is and its id.
KIND_TAG = "kind"
ID_TAG = "id"
SHARE_KIND = "share"
CANDIDATE_INVITE_KIND = "candidate_invite"
