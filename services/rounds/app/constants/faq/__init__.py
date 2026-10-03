from importlib import import_module

from prepza_common.constants import LANGUAGES

# Every language's FAQ, by code.
FAQS = {code: import_module(f"app.constants.faq.{code}").FAQ for code in LANGUAGES}
