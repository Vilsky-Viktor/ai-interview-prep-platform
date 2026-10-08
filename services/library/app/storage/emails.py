from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.constants.emails import (
    CONSENT_TEXT_VERSION,
    DEFAULTS,
    ConsentBasis,
    ConsentSource,
    EmailSetting,
)
from app.models.emails import EmailConsent, EmailPreferences
from app.storage.db import Session


def as_dict(row: EmailPreferences | None) -> dict[str, bool]:
    if row is None:
        return dict(DEFAULTS)

    return {setting: getattr(row, setting) for setting in EmailSetting}


async def preferences(user_id: str) -> dict[str, bool]:
    async with Session() as session:
        return as_dict(await session.get(EmailPreferences, user_id))


async def change(
    user_id: str, changes: dict[EmailSetting, bool], source: ConsentSource
) -> dict[str, bool]:
    """Applies the changes and logs each one that changes something, so a repeated request
    logs nothing twice. The row is locked, so concurrent changes don't miss each other.

    A sign-in turns updates on only for a user without a row yet, the first time they see the
    opt-out: it never turns them back on for someone who turned them off."""
    async with Session() as session:
        created = await session.scalar(
            insert(EmailPreferences)
            .values(user_id=user_id)
            .on_conflict_do_nothing()
            .returning(EmailPreferences.user_id)
        )
        row = await session.get(EmailPreferences, user_id, with_for_update=True)

        for setting, on in changes.items():
            soft_opt_in = source == ConsentSource.SIGN_IN and setting == EmailSetting.UPDATES and on

            if getattr(row, setting) == on or (soft_opt_in and created is None):
                continue

            setattr(row, setting, on)
            row.updated_at = datetime.now(UTC)
            session.add(
                EmailConsent(
                    user_id=user_id,
                    setting=setting,
                    granted=on,
                    source=source,
                    basis=ConsentBasis.SOFT_OPT_IN if soft_opt_in else ConsentBasis.CHOICE,
                    text_version=CONSENT_TEXT_VERSION,
                )
            )

        await session.commit()

        return as_dict(row)


async def consents(user_id: str) -> list[dict]:
    """The user's consent log, oldest first."""
    query = (
        select(EmailConsent)
        .where(EmailConsent.user_id == user_id)
        .order_by(EmailConsent.created_at, EmailConsent.id)
    )

    async with Session() as session:
        rows = (await session.scalars(query)).all()

    return [
        {
            "setting": row.setting,
            "granted": row.granted,
            "source": row.source,
            "basis": row.basis,
            "text_version": row.text_version,
            "at": row.created_at,
        }
        for row in rows
    ]
