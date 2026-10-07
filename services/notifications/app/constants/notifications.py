# A few short queries per request (streams hold no connection), so a small pool: 4 per instance,
# as infra/terraform/locals.tf budgets it.
DB_POOL_SIZE = 2
DB_MAX_OVERFLOW = 2
# The bell shows the latest few. A recipient keeps at most MAX_PER_RECIPIENT, none older than
# KEEP_DAYS.
DROPDOWN_LIMIT = 10
MAX_PER_RECIPIENT = 100
KEEP_DAYS = 90
# Each new notification removes up to this many expired ones (and their received events), which
# keeps up with how many arrive.
EXPIRED_PER_PRUNE = 100
# Kinds that can come in bursts. One about the same thing (its page and title) within
# GROUP_HOURS of the last adds to it, "3 candidates finished …", instead of a new one.
GROUPED_KINDS = {
    "candidate_finished",
    "invite_undelivered",
    "question_flagged",
    "question_fixed",
    "ats_not_invited",
}
GROUP_HOURS = 24
# A user's open tabs hear about a recipient's new notification on this Redis channel.
CHANNEL = "notifications:{recipient}:{recipient_id}"
# A stream sends a comment this often, so proxies (nginx, the load balancer) don't close it as
# idle.
HEARTBEAT_SECONDS = 20
