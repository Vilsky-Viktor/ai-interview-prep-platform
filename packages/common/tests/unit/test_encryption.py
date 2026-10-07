import pytest
from cryptography.fernet import Fernet
from prepza_common.encryption import decrypt, encrypt


def test_a_sealed_secret_is_unreadable_with_another_key():
    key = Fernet.generate_key().decode()
    sealed = encrypt(key, "secret-token")

    assert "secret-token" not in sealed
    assert decrypt(key, sealed) == "secret-token"
    assert decrypt(Fernet.generate_key().decode(), sealed) is None


@pytest.mark.parametrize("key", ["", "not-a-fernet-key"])
def test_a_missing_or_broken_key_reads_nothing(key):
    sealed = encrypt(Fernet.generate_key().decode(), "secret-token")

    assert decrypt(key, sealed) is None
