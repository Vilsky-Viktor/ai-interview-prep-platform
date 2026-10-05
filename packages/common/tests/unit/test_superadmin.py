import pytest
from fastapi import HTTPException
from prepza_common.superadmin import is_superadmin, superadmin_user
from prepza_common.user import User


def user(email="Ann@Example.com", verified=True):
    return User(uid="ann", email=email, email_verified=verified)


@pytest.fixture(autouse=True)
def admins(monkeypatch):
    monkeypatch.setenv("SUPERADMIN_EMAILS", " ann@example.com, bob@example.com ")


def test_a_listed_verified_email_is_a_superadmin_whatever_its_case():
    assert is_superadmin(user())


def test_an_unverified_or_unlisted_account_is_not():
    assert not is_superadmin(user(verified=False))
    assert not is_superadmin(user("eve@example.com"))


def test_no_admins_when_the_setting_is_empty(monkeypatch):
    monkeypatch.setenv("SUPERADMIN_EMAILS", "")

    assert not is_superadmin(user(""))


def test_admin_routes_are_not_found_for_others():
    with pytest.raises(HTTPException) as refused:
        superadmin_user(user("eve@example.com"))

    assert refused.value.status_code == 404
    assert superadmin_user(user()).uid == "ann"
