# Asks the model for a conversation's title in the history.
TITLE_SYSTEM = """\
Write a title for this conversation between a user and prepza's assistant: one line of at most \
{length} characters that sums up the whole conversation, in {language}. Company and interview \
names are fine; never include email addresses, phone numbers or candidates' names. No quotes \
and no period at the end. Reply with the title only."""
