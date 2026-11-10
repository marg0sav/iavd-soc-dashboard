from datetime import date, timedelta


class Period:
    """Периоды статистики."""

    DAY = "24 часа"
    WEEK = "7 дней"
    MONTH = "30 дней"
    YEAR = "Год"
    ALL_TIME = "Весь период"
    CUSTOM = "Свой период"


# Периоды переключателей статистики
PERIOD_OPTIONS = [Period.DAY, Period.WEEK, Period.MONTH, Period.YEAR, Period.ALL_TIME]


def period_to_date_range(period: str, today: date) -> tuple[date, date]:
    # Длина пресета в днях, включая сегодняшний
    PERIOD_DAYS = {
        Period.DAY: 1,
        Period.WEEK: 7,
        Period.MONTH: 30,
        Period.YEAR: 365,
    }

    if period not in PERIOD_DAYS:
        raise ValueError(f"Выбран невалидный период: {period!r}.")

    days_delta = PERIOD_DAYS[period] - 1
    return (today - timedelta(days=days_delta), today)
