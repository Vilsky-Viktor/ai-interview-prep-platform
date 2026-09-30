from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str
    smtp_host: str
    smtp_port: int = 25
    mail_from: str = "prepza. <no-reply@prepza.local>"
    # Public address of the site, used for links in emails.
    site_url: str


settings = Settings()
