from app.helpers.gifts import gift_key, inbox_of


def test_tags_case_and_gmail_dots_are_one_inbox():
    assert inbox_of(" Ann.Lee+2@GMail.com ") == "annlee@gmail.com"
    assert inbox_of("annlee@googlemail.com") == "annlee@gmail.com"
    assert gift_key("welcome", "ann.lee+x@gmail.com") == gift_key("welcome", "annlee@gmail.com")


def test_dots_count_outside_gmail():
    assert inbox_of("ann.lee+jobs@acme.com") == "ann.lee@acme.com"
    assert gift_key("welcome", "ann.lee@acme.com") != gift_key("welcome", "annlee@acme.com")
