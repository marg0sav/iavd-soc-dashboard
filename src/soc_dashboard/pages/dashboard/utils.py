from datetime import date, datetime


def tgb_date_range_to_date(value) -> date | None:
    """Приводит значение из tgb.date_range к date, None - если даты нет."""
    # Браузер присылает date, а стартовое значение задаётся как datetime
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return None
