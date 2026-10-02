from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # With a Resend key emails go out through Resend; without one, to the SMTP server (mailpit).
    resend_api_key: str = ""
    # Signs Resend's webhooks (bounces, complaints); without it every webhook is refused.
    resend_webhook_secret: str = ""
    smtp_host: str = "mailpit"
    smtp_port: int = 25
    # Resend sends only from a domain verified in its dashboard.
    mail_from: str = "prepza. <no-reply@prepza.local>"
    # Public address of the site, used for links in emails.
    site_url: str
    # The services that own invites, told when an invite's email wasn't delivered.
    companies_url: str
    library_url: str


settings = Settings()
