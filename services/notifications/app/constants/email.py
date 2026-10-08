RESEND_EMAILS_URL = "https://api.resend.com/emails"
SEND_TIMEOUT_S = 10
# Resend's answers that no retry can change: a malformed request or an address it won't send to.
# Rate limits (resend.ResendBusy), outages and a wrong API key are retried instead.
RESEND_REFUSED = (400, 422)
