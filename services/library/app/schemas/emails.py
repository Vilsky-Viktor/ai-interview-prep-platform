from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.constants.emails import ConsentSource, EmailSetting


class EmailPreferencesOut(BaseModel):
    candidate_finished: bool
    invite_undelivered: bool
    ats_not_invited: bool
    interview_ready: bool
    reminders: bool
    updates: bool
    promotions: bool


class EmailPreferencesIn(BaseModel):
    """Only the settings to change; the rest stay as they are."""

    changes: dict[EmailSetting, bool] = Field(min_length=1)
    source: Literal[ConsentSource.SIGN_IN, ConsentSource.SETTINGS]

    @model_validator(mode="after")
    def sign_in_sets_only_marketing(self) -> "EmailPreferencesIn":
        # Signing in shows the updates opt-out and an unticked promotions box: it may set updates
        # either way, and only turn promotions on.
        if self.source == ConsentSource.SIGN_IN and any(
            setting not in (EmailSetting.UPDATES, EmailSetting.PROMOTIONS)
            or (setting == EmailSetting.PROMOTIONS and not on)
            for setting, on in self.changes.items()
        ):
            raise ValueError("Signing in may only set updates and turn on promotions.")

        return self
