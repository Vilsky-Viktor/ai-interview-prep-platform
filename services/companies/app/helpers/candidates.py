def candidate_key(interview_id, email: str) -> str:
    """Names the credits billing sets aside for one candidate of one interview."""
    return f"{interview_id}:{email.lower()}"
