from unittest import mock

from prepza_common import db
from prepza_common.constants import DB_POOL_RECYCLE_SECONDS


def test_pooled_connections_are_replaced_by_age_not_pinged_on_every_use():
    with mock.patch.object(db, "create_async_engine") as create:
        db.database("postgresql+psycopg://user@/name", pool_size=2, max_overflow=1)

    options = create.call_args.kwargs
    assert options["pool_recycle"] == DB_POOL_RECYCLE_SECONDS
    assert "pool_pre_ping" not in options
    assert (options["pool_size"], options["max_overflow"]) == (2, 1)
