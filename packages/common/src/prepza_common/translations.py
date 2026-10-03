# Messages the services show users, by language, keyed by the English text they're raised with:
# one module per language in messages/. A message missing there is shown in English.
from importlib import import_module

from prepza_common.constants import DEFAULT_LANGUAGE, LANGUAGES

TRANSLATIONS = {
    code: import_module(f"prepza_common.messages.{code}").MESSAGES
    for code in LANGUAGES
    if code != DEFAULT_LANGUAGE
}
