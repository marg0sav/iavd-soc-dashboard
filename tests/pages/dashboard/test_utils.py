from datetime import date, datetime

import pytest

from soc_dashboard.pages.dashboard.utils import tgb_date_range_to_date


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # Так дату присылает браузер из tgb.date_range
        pytest.param(date(2024, 1, 10), date(2024, 1, 10), id="date"),
        # Так задаётся стартовое значение в default_summary_dates
        pytest.param(datetime(2024, 1, 10, 0, 0), date(2024, 1, 10), id="datetime"),
        pytest.param(None, None, id="none"),
        # Пустое поле Taipy присылает строкой "None"
        pytest.param("None", None, id="none_string"),
    ],
)
def test_to_date(value, expected):
    assert tgb_date_range_to_date(value) == expected
