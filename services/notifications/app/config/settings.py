from prepza_common.settings import ServiceSettings


class Settings(ServiceSettings):
    # The API description lists every route, internal ones too: development only.
    api_docs: bool = False
    # The bell's notifications; Redis tells every open tab of a recipient at once.
    database_url: str
    redis_url: str
    # Signs calls from other services (library deletes and exports a user's notifications).
    service_secret: str
    # With a Resend key emails go out through Resend; without one, to the SMTP server (mailpit).
    resend_api_key: str = ""
    # Signs Resend's webhooks (bounces, complaints); without it every webhook is refused.
    resend_webhook_secret: str = ""
    smtp_host: str = "mailpit"
    smtp_port: int = 25
    # Resend sends only from a domain verified in its dashboard.
    mail_from: str = "prepza. <no-reply@prepza.local>"
    # prepza's inbox: the contact page's messages go here.
    contact_email: str = "hello@prepza.ai"
    # Public address of the site, used for links in emails.
    site_url: str
    # Companies owns the invites, told when an invite's email wasn't delivered, and says which
    # companies a user belongs to, whose notifications they see.
    companies_url: str

    @property
    def sqlalchemy_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)


settings = Settings()
