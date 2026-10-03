import pytest

from app.helpers.language import text_language


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Senior backend developer: Python, PostgreSQL, Kubernetes.", "en"),
        # A Russian job description full of Latin tech terms is still Russian.
        ("Ищем Senior Python разработчика: Django, FastAPI, PostgreSQL, Redis, Docker.", "ru"),
        ("Python, Django, PostgreSQL — опыт от 3 лет", "ru"),
        # An English one naming a Russian city stays English.
        (
            "Backend engineer in our Москва office: Python, SQL and cloud infrastructure.",
            "en",
        ),
    ],
)
def test_the_pasted_text_decides_the_language(text, expected):
    # The interface's language is the other one, and doesn't matter.
    other = "ru" if expected == "en" else "en"

    assert text_language(text, other) == expected


def test_a_text_without_letters_takes_the_interfaces_language():
    assert text_language("123 — 456", "ru") == "ru"
