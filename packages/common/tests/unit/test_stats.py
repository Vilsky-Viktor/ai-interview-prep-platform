from datetime import UTC, datetime

from prepza_common.stats import month_range


def test_a_month_runs_to_the_start_of_the_next():
    assert month_range("2026-02") == (
        datetime(2026, 2, 1, tzinfo=UTC),
        datetime(2026, 3, 1, tzinfo=UTC),
    )


def test_december_runs_into_the_new_year():
    assert month_range("2025-12")[1] == datetime(2026, 1, 1, tzinfo=UTC)
