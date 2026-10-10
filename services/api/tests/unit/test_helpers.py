import hashlib
import hmac
import json
import socket
from datetime import UTC, datetime

import pytest
from prepza_common.tokens import hashed

from app.helpers import webhooks
from app.helpers.keys import add_months, expired, new_key
from app.helpers.webhooks import body_of, public_address, signature


def test_a_new_key_is_kept_only_as_its_hash():
    key, shown, stored = new_key()

    assert key.startswith("pz_") and len(key) > 30
    assert key.startswith(shown) and len(shown) == 10
    assert stored == hashlib.sha256(key.encode()).hexdigest() == hashed(key)
    assert new_key()[0] != key


def test_a_key_expires_at_its_time_and_one_without_never_does():
    now = datetime(2026, 10, 8, tzinfo=UTC)

    assert not expired(None, now)
    assert not expired(datetime(2026, 10, 9, tzinfo=UTC), now)
    assert expired(now, now)


@pytest.mark.parametrize(
    ("start", "months", "end"),
    [
        (datetime(2026, 10, 8, 12, 30, tzinfo=UTC), 1, datetime(2026, 11, 8, 12, 30, tzinfo=UTC)),
        (datetime(2026, 10, 8, tzinfo=UTC), 3, datetime(2027, 1, 8, tzinfo=UTC)),
        (datetime(2026, 1, 31, tzinfo=UTC), 1, datetime(2026, 2, 28, tzinfo=UTC)),
        (datetime(2027, 12, 31, tzinfo=UTC), 12, datetime(2028, 12, 31, tzinfo=UTC)),
    ],
)
def test_months_are_calendar_months(start, months, end):
    assert add_months(start, months) == end


def test_a_web_hook_is_signed_over_its_time_and_raw_body():
    body = body_of("e1", "candidate.finished", {"a": 1})
    expected = hmac.new(b"whsec_x", b"1760000000." + body, hashlib.sha256).hexdigest()

    assert json.loads(body) == {"id": "e1", "type": "candidate.finished", "data": {"a": 1}}
    assert signature("whsec_x", 1760000000, body) == f"t=1760000000,v1={expected}"


@pytest.mark.parametrize(
    ("url", "addresses", "address"),
    [
        ("https://example.com/hook", ["93.184.216.34", "2606:2800::1"], "93.184.216.34"),
        ("http://example.com/hook", ["93.184.216.34"], None),
        ("https://localhost/hook", ["127.0.0.1"], None),
        ("https://metadata/hook", ["169.254.169.254"], None),
        ("https://intranet/hook", ["10.0.0.5"], None),
        ("https://split/hook", ["93.184.216.34", "192.168.1.2"], None),
    ],
)
def test_only_https_to_the_public_internet_and_the_address_checked(
    monkeypatch, url, addresses, address
):
    def resolve(host, port, proto=0):
        return [(socket.AF_INET, 1, 6, "", (address, port)) for address in addresses]

    monkeypatch.setattr(webhooks.socket, "getaddrinfo", resolve)

    assert public_address(url) == address


def test_a_failed_lookup_raises_so_the_send_is_retried(monkeypatch):
    def resolve(host, port, proto=0):
        raise socket.gaierror

    monkeypatch.setattr(webhooks.socket, "getaddrinfo", resolve)

    with pytest.raises(socket.gaierror):
        public_address("https://unknown/hook")
