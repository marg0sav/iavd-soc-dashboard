class Col:
    """Названия столбцов исходного датасета инцидентов."""

    ID = "EntityId"
    CREATED = "Создан"
    DATE = "Дата"
    CLOSED_AT = "Дата закрытия (факт)"
    INCIDENT_TYPE = "Тип инцидента"
    SEVERITY = "Критичность"
    VERDICT = "Вердикт"
    ASSIGNEE = "Ответственный"


# Столбцы с датами, которые приводятся к datetime при загрузке
DATETIME_COLUMNS = (Col.CREATED, Col.DATE, Col.CLOSED_AT)

# Значение фильтра, при котором фильтрация не применяется
ALL = "Все"

# Значение, которое показывается вместо пустого или неопределённого
NO_DATA = "—"


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

# Столбцы таблицы карточки инцидента
CARD_FIELD = "Поле"
CARD_VALUE = "Значение"
CARD_COLUMNS = [CARD_FIELD, CARD_VALUE]
