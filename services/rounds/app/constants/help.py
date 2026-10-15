import re
from enum import StrEnum


class HelpRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


# Legal documents the help routes serve, by the path they're asked for under.
class LegalDocument(StrEnum):
    TERMS = "terms"
    PRIVACY = "privacy"
    DPA = "dpa"


# The page keeps the conversation and sends it whole; nothing of it is stored. A new question's
# length, the bounds on what's sent, and the earlier messages the model sees with a question.
MAX_HELP_QUESTION_LENGTH = 1_000
MAX_HELP_MESSAGE_LENGTH = 10_000
# A reply's signature: SHA-256, in hex.
SIGNATURE_LENGTH = 64
MAX_HELP_MESSAGES = 200
HELP_HISTORY_MESSAGES = 10
# The page's conversation can't be checked, so the model sees at most this many characters of
# it before the question, the latest messages first.
HELP_HISTORY_CHARACTERS = 8_000
# Help chat questions an hour from one visitor's address. Cloud Armor limits each address too;
# this holds wherever the service runs.
HELP_IP_LIMIT = 60
# An answer's longest, in tokens (its reasoning included), and the tokens all help chats may use
# in a day together (input and output, counted after each answer): a ceiling on what the public
# chat costs. A spent budget refuses new questions (429); a started answer always finishes.
HELP_MAX_OUTPUT_TOKENS = 1_500
HELP_TOKENS_PER_DAY = 50_000_000
HELP_SPEND_KEY = "spend:help:all"
# How long billing's prices are kept for the FAQ and the chat before they're asked again.
CATALOG_KEY = "billing-catalog"
CATALOG_CACHE_SECONDS = 5 * 60
LAST_NOT_QUESTION = "The conversation must end with a question."
QUESTION_TOO_LONG = "The question is too long."

# The FAQ's example of a small company's hiring, in candidates a month, priced over a year.
FAQ_EXAMPLE_CANDIDATES = 5
# How long the platform guide (GET /help/guide) is kept, per language, before it's built again.
GUIDE_CACHE_SECONDS = CATALOG_CACHE_SECONDS
# A reply to a visitor asking to sign in or sign up starts with this marker (the prompt says
# so), naming the way they asked for if any; the chat sends a sign-in card in its place.
SIGN_IN_MARKER = re.compile(r"^\s*\[\[sign_in(?::(google|linkedin|github))?\]\]\s*")
SIGN_IN_PREFIX = "[[sign_in"

# The FAQ names today's prices; without them (billing not answering) it isn't served.
PRICES_UNAVAILABLE = "Prices aren't available right now. Please try again in a minute."
