from unittest import mock

import pytest
from fastapi import HTTPException
from firebase_admin import auth as firebase_auth
from prepza_common.auth import verify
from prepza_common.constants import SIGN_IN_UNAVAILABLE

CLAIMS = {"uid": "ann", "email": "ann@example.com", "email_verified": True, "name": "Ann"}


def test_a_valid_token_gives_its_user():
    with mock.patch.object(firebase_auth, "verify_id_token", return_value=CLAIMS):
        user = verify("token")

    assert (user.uid, user.email, user.email_verified, user.name) == (
        "ann",
        "ann@example.com",
        True,
        "Ann",
    )


@pytest.mark.parametrize(
    "error", [ValueError("malformed"), firebase_auth.InvalidIdTokenError("bad", cause=None)]
)
def test_an_invalid_token_gives_no_user(error):
    with mock.patch.object(firebase_auth, "verify_id_token", side_effect=error):
        assert verify("token") is None


def test_unreachable_certificates_are_a_503_not_a_bad_token():
    error = firebase_auth.CertificateFetchError("down", cause=None)

    with (
        mock.patch.object(firebase_auth, "verify_id_token", side_effect=error),
        pytest.raises(HTTPException) as raised,
    ):
        verify("token")

    assert raised.value.status_code == 503
    assert raised.value.detail == SIGN_IN_UNAVAILABLE


def test_a_signed_in_request_names_the_user_to_sentry_by_id_only():
    from fastapi.security import HTTPAuthorizationCredentials
    from prepza_common.auth import current_user

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

    with (
        mock.patch.object(firebase_auth, "verify_id_token", return_value=CLAIMS),
        mock.patch("sentry_sdk.set_user") as set_user,
    ):
        current_user(credentials)

    set_user.assert_called_once_with({"id": "ann"})
