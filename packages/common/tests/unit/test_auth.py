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
