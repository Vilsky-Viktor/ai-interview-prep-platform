import pytest
from prepza_common.client_ip import client_ip
from starlette.requests import Request


def request(forwarded: str | None) -> Request:
    headers = [(b"x-forwarded-for", forwarded.encode())] if forwarded is not None else []

    return Request({"type": "http", "headers": headers, "client": ("10.0.0.9", 1234)})


@pytest.mark.parametrize(
    ("forwarded", "expected"),
    [
        # The load balancer appends "<client>,<load balancer>": what came before is made up.
        ("1.1.1.1, 2.2.2.2, 35.0.0.1", "2.2.2.2"),
        ("2.2.2.2, 35.0.0.1", "2.2.2.2"),
        # Locally, without the load balancer: the connection's address.
        ("2.2.2.2", "10.0.0.9"),
        (None, "10.0.0.9"),
    ],
)
def test_the_visitor_is_the_address_the_load_balancer_saw(forwarded, expected):
    assert client_ip(request(forwarded)) == expected
