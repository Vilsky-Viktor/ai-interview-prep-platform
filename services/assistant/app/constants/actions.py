# The assistant's actions: user-facing routes that change something, as tools. The model only
# prepares one; it runs when the user confirms its card in the panel, with exactly the arguments
# the card showed. Entries are like the reads' (constants/tools.py), and:
# - method: POST, PUT, PATCH or DELETE, with confirm: True (the loader refuses one without);
# - body: the JSON body's fields the model may set;
# - preview: the arguments the card shows (the body's fields when left out);
# - subject: what the action is about, read with the user's token when it's prepared, so the
#   card names it (a company's name, an interview's title): its service, path (filled from the
#   arguments), `query` arguments, the `field` to show and, for a list, the argument whose
#   item it is (`match`);
# - destructive: the card warns that it can't be undone;
# - render and link: the page the result opens (ids from the arguments and the result's data),
#   and result_label: the result's field naming it.

from app.constants.account_actions import ACCOUNT_ACTIONS
from app.constants.company_actions import COMPANY_ACTIONS
from app.constants.interview_actions import INTERVIEW_ACTIONS

ACTIONS = {**COMPANY_ACTIONS, **INTERVIEW_ACTIONS, **ACCOUNT_ACTIONS}
