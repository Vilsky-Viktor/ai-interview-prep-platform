import uuid

import pytest
from fastapi import HTTPException

from app.integrations import companies

EDITORS = ("owner", "admin")


def interview(company_id, title="Accountant", ready=True, interview_id=None) -> dict:
    """An interview as companies' GET /internal/interviews returns it."""
    return {
        "id": str(interview_id or uuid.uuid4()),
        "company_id": str(company_id),
        "title": title,
        "ready": ready,
    }


@pytest.fixture
def companies_api(monkeypatch):
    """The companies service, faked: members' roles by (company, user), interviews by id, and
    the invites it sent (or the status it refuses them with)."""
    state = {"roles": {}, "interviews": {}, "sent": [], "refuse": None}

    async def access(company_id, user_id):
        role = state["roles"].get((company_id, user_id))

        return {"member": role is not None, "editor": role in EDITORS}

    async def interviews(ids):
        return {item: state["interviews"][item] for item in ids if item in state["interviews"]}

    async def invite(interview_id, email, sender_id, name=None):
        if state["refuse"]:
            raise HTTPException(state["refuse"])

        state["sent"].append((email, sender_id))
        state.setdefault("names", {})[email] = name

        return uuid.uuid4()

    monkeypatch.setattr(companies, "access", access)
    monkeypatch.setattr(companies, "interviews", interviews)
    monkeypatch.setattr(companies, "invite", invite)

    return state
