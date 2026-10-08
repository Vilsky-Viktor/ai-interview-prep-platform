# The assistant's actions: user-facing routes that change something, as tools. The model only
# prepares one; it runs when the user confirms its card in the panel, with exactly the arguments
# the card showed. Entries are like the reads' (constants/tools.py), and:
# - method: POST, PUT, PATCH or DELETE, with confirm: True (the loader refuses one without);
# - body: the JSON body's fields the model may set;
# - preview: the arguments the card shows (the body's fields when left out); ids are shown by
#   the panel as names where it can;
# - destructive: the card warns that it can't be undone;
# - render and link: the page the result opens (ids from the arguments and the result's data).

ACTIONS = {
    "create_company": {
        "service": "companies",
        "method": "POST",
        "path": "/companies",
        "params": [],
        "body": ["name"],
        "confirm": True,
        "description": (
            "Create a company the user will own (needs only its name). Prepares it: it runs "
            "once the user confirms it in the panel."
        ),
        "fields": ["id", "name", "role"],
        "render": "link",
        "link": "/companies/{id}/interviews",
    },
}
