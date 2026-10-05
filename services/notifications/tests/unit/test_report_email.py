import asyncio
import base64
import json

import httpx

from app.config.settings import settings
from app.helpers.emails import candidate_invite_email, candidate_reminder_email, report_email
from app.integrations import resend, smtp

PDF = base64.b64encode(b"%PDF-1.3 a report").decode()
DATA = {
    "email": "boss@example.com",
    "sender": "Bob",
    "reply_to": "bob@example.com",
    "company": "Arcolabs",
    "title": "Backend",
    "candidate": "ann@example.com",
    "language": "en",
    "filename": "Report ann@example.com.pdf",
    "pdf": PDF,
}


def test_the_report_email_carries_the_pdf_and_replies_go_to_the_sender():
    email = report_email(DATA, "https://prepza.com")

    assert email.to == "boss@example.com"
    assert email.subject == "Bob shared a candidate report: ann@example.com"
    assert email.reply_to == "bob@example.com"
    assert email.attachments == [("Report ann@example.com.pdf", PDF)]
    # The PDF travels as an attachment only; its own reason for being sent is in the footer.
    assert PDF not in email.html and PDF not in email.text
    assert "Bob shared a candidate report with this address" in email.text


def test_the_report_of_all_candidates_has_its_own_text():
    data = {key: value for key, value in DATA.items() if key != "candidate"}
    data |= {"kind": "candidates", "language": "en", "filename": "Candidates Backend.pdf"}

    email = report_email(data, "https://prepza.com")

    assert email.subject == "Bob shared a report of all candidates: Backend"
    assert email.attachments == [("Candidates Backend.pdf", PDF)]
    assert "Bob shared a candidates report with this address" in email.text


def test_resend_gets_the_attachment(monkeypatch):
    sent = {}

    def answer(request):
        sent.update(json.loads(request.content))

        return httpx.Response(200, json={"id": "e-1"})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        resend.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(answer), **kwargs),
    )
    monkeypatch.setattr(settings, "resend_api_key", "re_test")

    asyncio.run(resend.send(report_email(DATA, ""), "k"))

    assert sent["attachments"] == [{"filename": "Report ann@example.com.pdf", "content": PDF}]
    assert sent["reply_to"] == "bob@example.com"


def test_smtp_attaches_the_pdf(monkeypatch):
    sent = []

    class FakeSMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def send_message(self, message):
            sent.append(message)

    monkeypatch.setattr(smtp.smtplib, "SMTP", FakeSMTP)

    smtp.send_sync(report_email(DATA, ""))

    [attachment] = list(sent[0].iter_attachments())
    assert attachment.get_filename() == "Report ann@example.com.pdf"
    assert attachment.get_content() == b"%PDF-1.3 a report"


def test_a_reminder_opens_the_same_invite_and_is_tagged_like_it():
    data = {
        "invite_id": "i-1",
        "email": "ann@example.com",
        "token": "abc",
        "title": "Backend",
        "company": "Acme",
        "language": "en",
    }

    reminder = candidate_reminder_email(data, "https://prepza.com")

    assert reminder.subject == "Reminder: Acme is waiting for your interview"
    assert "https://prepza.com/invite/abc" in reminder.text
    assert reminder.tags == candidate_invite_email(data, "https://prepza.com").tags


def test_an_invite_from_a_company_with_a_logo_shows_it_at_the_top():
    data = {
        "invite_id": "i-1",
        "email": "ann@example.com",
        "token": "abc",
        "title": "Backend",
        "company": "Acme & Co",
        "language": "en",
        "logo_path": "/api/companies/companies/c-1/logo?v=2",
    }

    with_logo = candidate_invite_email(data, "https://prepza.com/")
    without = candidate_invite_email({**data, "logo_path": None}, "https://prepza.com/")

    assert (
        '<img src="https://prepza.com/api/companies/companies/c-1/logo?v=2" alt="Acme &amp; Co"'
        in with_logo.html
    )
    assert "<img" not in without.html
