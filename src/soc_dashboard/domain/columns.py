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
