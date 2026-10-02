from sqlalchemy import delete, or_, select, union

from app.constants.sets import OwnerType, SetKind
from app.models.feedback import PreparationRating, QuestionRating, QuestionReport
from app.models.sets import QuestionSet
from app.models.sharing import JoinedPreparation, ShareInvite
from app.storage import stats
from app.storage.db import Session


async def owned_preparations(user_id: str) -> list:
    query = select(QuestionSet.id).where(
        QuestionSet.kind == SetKind.PREPARATION,
        QuestionSet.owner_type == OwnerType.USER,
        QuestionSet.owner_id == user_id,
    )

    async with Session() as session:
        return list(await session.scalars(query))


async def delete_user(user_id: str, email: str) -> None:
    """The user's ratings, reports, joins and shares; ratings and join counts of the
    preparations they touched are recounted. Their own preparations are deleted before this."""
    email = email.lower()
    touched = union(
        select(PreparationRating.set_id).where(PreparationRating.user_id == user_id),
        select(JoinedPreparation.set_id).where(JoinedPreparation.user_id == user_id),
    )

    async with Session() as session:
        set_ids = list(await session.scalars(touched))

        for model in (PreparationRating, QuestionRating, QuestionReport, JoinedPreparation):
            await session.execute(delete(model).where(model.user_id == user_id))

        await session.execute(
            delete(ShareInvite).where(
                or_(
                    ShareInvite.invited_by == user_id,
                    ShareInvite.accepted_by == user_id,
                    ShareInvite.email == email,
                )
            )
        )

        for set_id in set_ids:
            await stats.recount(session, set_id)

        await session.commit()


async def export(user_id: str, email: str) -> dict:
    email = email.lower()

    async with Session() as session:
        owned = await session.execute(
            select(QuestionSet.title, QuestionSet.visibility, QuestionSet.created_at).where(
                QuestionSet.kind == SetKind.PREPARATION,
                QuestionSet.owner_type == OwnerType.USER,
                QuestionSet.owner_id == user_id,
            )
        )
        joined = await session.execute(
            select(QuestionSet.title, JoinedPreparation.joined_at)
            .join(QuestionSet, QuestionSet.id == JoinedPreparation.set_id)
            .where(JoinedPreparation.user_id == user_id)
        )
        ratings = await session.execute(
            select(QuestionSet.title, PreparationRating.value)
            .join(QuestionSet, QuestionSet.id == PreparationRating.set_id)
            .where(PreparationRating.user_id == user_id)
        )
        votes = await session.execute(
            select(QuestionRating.question_id, QuestionRating.value).where(
                QuestionRating.user_id == user_id
            )
        )
        reports = await session.execute(
            select(
                QuestionReport.question_id,
                QuestionReport.reason,
                QuestionReport.comment,
                QuestionReport.created_at,
            ).where(QuestionReport.user_id == user_id)
        )
        shares = await session.execute(
            select(QuestionSet.title, ShareInvite.email, ShareInvite.created_at)
            .join(QuestionSet, QuestionSet.id == ShareInvite.set_id)
            .where(or_(ShareInvite.invited_by == user_id, ShareInvite.email == email))
        )

        return {
            "own_preparations": [
                {"title": title, "visibility": visibility, "created_at": at}
                for title, visibility, at in owned
            ],
            "joined_preparations": [{"title": title, "joined_at": at} for title, at in joined],
            "preparation_ratings": [{"title": title, "stars": value} for title, value in ratings],
            "question_votes": [{"question_id": qid, "vote": value} for qid, value in votes],
            "question_reports": [
                {"question_id": qid, "reason": reason, "comment": comment, "at": at}
                for qid, reason, comment, at in reports
            ],
            "shares": [
                {"preparation": title, "email": address, "at": at} for title, address, at in shares
            ],
        }
