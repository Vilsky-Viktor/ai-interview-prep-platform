# The invite emails' texts in every language an interview or kit can be written in
# (prepza_common.constants.CONTENT_LANGUAGES), one module each. None of them needs the inviter's
# gender: past-tense or gendered verbs are avoided.

from app.templates.languages import ar, de, en, es, fa, fr, he, it, nl, pl, pt, ru, tr, uk

EMAILS = {
    "en": en.TEXTS,
    "ru": ru.TEXTS,
    "uk": uk.TEXTS,
    "es": es.TEXTS,
    "pt": pt.TEXTS,
    "de": de.TEXTS,
    "fr": fr.TEXTS,
    "it": it.TEXTS,
    "pl": pl.TEXTS,
    "nl": nl.TEXTS,
    "tr": tr.TEXTS,
    "ar": ar.TEXTS,
    "he": he.TEXTS,
    "fa": fa.TEXTS,
}
