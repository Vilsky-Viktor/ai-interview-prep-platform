# The most questions a template's public sample shows (routers/templates.py).
SAMPLE_QUESTIONS = 5

# A slug is cut to this many characters before "-2", "-3"… is added; the column holds 120.
SLUG_LENGTH = 80

# The slug of a template whose title has no ASCII letters or digits.
FALLBACK_SLUG = "template"

# Slugs a template never gets: the words of the other /templates/<word> routes (routers/templates.py).
RESERVED_SLUGS = {"filters", "copyable"}
