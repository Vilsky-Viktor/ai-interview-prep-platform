import hashlib
import hmac
import json
import time

SECRET = "pdl_ntfset_test_secret"


def completed(price_id="pri_candidates_10", owner_type="company", owner_id="acme", quantity=1):
    return {
        "event_type": "transaction.completed",
        "data": {
            "id": "txn_01",
            "currency_code": "USD",
            "custom_data": {"owner_type": owner_type, "owner_id": owner_id, "buyer_id": "ann"},
            "items": [{"price": {"id": price_id}, "quantity": quantity}],
            "details": {"totals": {"grand_total": "5000"}},
        },
    }


def signed(event: dict, secret=SECRET, at=None) -> tuple[bytes, str]:
    """The body and Paddle-Signature header Paddle would send."""
    body = json.dumps(event).encode()
    timestamp = str(int(at if at is not None else time.time()))
    digest = hmac.new(secret.encode(), f"{timestamp}:".encode() + body, hashlib.sha256)

    return body, f"ts={timestamp};h1={digest.hexdigest()}"
