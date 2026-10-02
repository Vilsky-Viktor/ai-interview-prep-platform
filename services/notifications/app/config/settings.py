from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str
    # With a Resend key emails go out through Resend; without one, to the SMTP server (mailpit).
    resend_api_key: str = ""
    smtp_host: str = "mailpit"
    smtp_port: int = 25
    # Resend sends only from a domain verified in its dashboard.
    mail_from: str = "prepza. <no-reply@prepza.local>"
    # Public address of the site, used for links in emails.
    site_url: str


settings = Settings()
