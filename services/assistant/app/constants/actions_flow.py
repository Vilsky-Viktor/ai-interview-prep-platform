# Pending actions: what the model prepared, waiting for the user's confirmation. Kept only in
# Redis, never in the database, and gone on confirm, cancel or after this long.
ACTION_TTL_SECONDS = 10 * 60
ACTION_KEY = "assistant:action:{action_id}"
# A user's pending actions, so deleting their account deletes them too.
USER_ACTIONS_KEY = "assistant:actions:user:{user_id}"

# The card's states, as the panel shows them.
PENDING = "pending"
DONE = "done"
FAILED = "failed"
CANCELLED = "cancelled"

# What the model reads after preparing one, and with the confirmed result (it isn't the user's
# text: the app tells the model).
PENDING_FOR_MODEL = (
    "Prepared, not done: the panel shows the user a card with exactly this action, and it runs "
    "only if they confirm it. Tell them in one sentence to check it and confirm."
)
CONFIRMED_NOTE = (
    "[From the app, not the user] The user confirmed the action {tool}; the service answered "
    "{result}. Tell them in one or two sentences what happened and, if it worked, the likely "
    "next step. Don't prepare another action unless they ask."
)

# What the user reads; translated by its English text.
ACTION_GONE = "This action expired or was already handled. Ask again to prepare it."
NOT_YOUR_COMPANY = "Company not found"
