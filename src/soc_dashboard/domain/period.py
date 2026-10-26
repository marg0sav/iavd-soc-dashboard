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
