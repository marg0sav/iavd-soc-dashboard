from datetime import date

import pytest

from soc_dashboard.domain.period import Period, period_to_date_range

TODAY = date(2025, 11, 20)


@pytest.mark.parametrize(
    ("period", "expected_from"),
    [
        pytest.param(Period.DAY, date(2025, 11, 20), id="day"),
        pytest.param(Period.WEEK, date(2025, 11, 14), id="week"),
        pytest.param(Period.MONTH, date(2025, 10, 22), id="month"),
        pytest.param(Period.YEAR, date(2024, 11, 21), id="year"),
    ],
)
def test_period_to_date_range(period, expected_from):
    # Сегодняшний день всегда входит в период
    assert period_to_date_range(period, TODAY) == (expected_from, TODAY)


@pytest.mark.parametrize("period", [Period.ALL_TIME, Period.CUSTOM])
def test_period_without_fixed_length(period):
    with pytest.raises(ValueError):
        period_to_date_range(period, TODAY)
