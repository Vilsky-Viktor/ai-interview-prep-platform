from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text


def test_every_migration_ran_on_a_fresh_database(run):
    from app.storage.db import engine

    async def current():
        async with engine.connect() as connection:
            return (
                await connection.execute(text("SELECT version_num FROM alembic_version"))
            ).scalar()

    assert run(current()) == ScriptDirectory.from_config(Config("alembic.ini")).get_current_head()
