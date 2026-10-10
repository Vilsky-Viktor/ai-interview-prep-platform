import hashlib

from prepza_common.tokens import hashed, new_token


def test_a_new_token_has_its_prefix_and_is_kept_only_as_its_hash():
    token, stored = new_token("pzm_", 32)

    assert token.startswith("pzm_") and len(token) > 40
    assert stored == hashlib.sha256(token.encode()).hexdigest() == hashed(token)
    assert new_token("pzm_", 32)[0] != token
