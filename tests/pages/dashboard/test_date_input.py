from datetime import date

import pytest

from soc_dashboard.pages.dashboard.utils import format_date_input, parse_date_input


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param("01012024", "01.01.2024", id="digits_only"),
        pytest.param("0101", "01.01", id="partial"),
        pytest.param("01.01.2024", "01.01.2024", id="already_formatted"),
        pytest.param("010120245", "01.01.2024", id="extra_digits_dropped"),
        pytest.param("", "", id="empty"),
        pytest.param(None, "", id="none"),
    ],
)
def test_format_date_input(value, expected):
    assert format_date_input(value) == expected


@pytest.mark.parametrize(
    ("value", "message"),
    [
        pytest.param("01a", "Разрешены только цифры и точки", id="invalid_input"),
    ],
)
def test_format_date_input_rejects_invalid(value, message):
    with pytest.raises(ValueError, match=message):
        format_date_input(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param("01.01.2024", date(2024, 1, 1), id="first_day_of_year"),
        pytest.param("15.03.2024", date(2024, 3, 15), id="regular"),
        pytest.param("29.02.2024", date(2024, 2, 29), id="leap_day"),
    ],
)
def test_parse_date_input(value, expected):
    assert parse_date_input(value) == expected


@pytest.mark.parametrize(
    ("value", "message"),
    [
        pytest.param("1.3.2024", "Введите дату полностью", id="incomplete"),
        pytest.param("", "Введите дату полностью", id="empty"),
        pytest.param("31.02.2024", "Указана несуществующая дата", id="nonexistent"),
    ],
)
def test_parse_date_input_rejects_invalid(value, message):
    with pytest.raises(ValueError, match=message):
        parse_date_input(value)
