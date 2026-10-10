"""SQL for one-off migrations that took candidates' emails out of the keys of their credits:
companies (an invite's hold_key) and billing (its holds and entries) rewrite their own copies of
a key, and must arrive at the same new one. Both get it here."""


def hashed(old: str) -> str:
    """The first 32 hex digits of the SHA-256 of `old`, an SQL text expression."""
    return f"left(encode(sha256(convert_to({old}, 'UTF8')), 'hex'), 32)"


def invite_key(interview_id: str, old: str) -> str:
    """Companies' new key for an invite: "{interview_id}:{hash of the old key}"."""
    return f"{interview_id}::text || ':' || {hashed(old)}"


def ledger_key(key: str) -> str:
    """Billing's new key for a "candidate:{interview_id}:{email}[:{uuid}]" hold or entry: the
    same as companies', after "candidate:"."""
    old = f"substr({key}, 11)"

    return f"'candidate:' || split_part({old}, ':', 1) || ':' || {hashed(old)}"
