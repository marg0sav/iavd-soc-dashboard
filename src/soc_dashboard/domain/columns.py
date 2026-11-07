class Col:
    """Названия столбцов исходного датасета инцидентов."""

    ID = "EntityId"
    CREATED = "Создан"
    DATE = "Дата"
    CLOSED_AT = "Дата закрытия (факт)"
    TAKEN_AT = "Дата взятия в работу"
    SLA_TAKE_OVERDUE = "SLA просрочен (взятие в работу)"
    INCIDENT_TYPE = "Тип инцидента"
    SEVERITY = "Критичность"
    VERDICT = "Вердикт"
    ASSIGNEE = "Ответственный"


# Столбцы с датами, которые приводятся к datetime при загрузке
DATETIME_COLUMNS = (
    Col.CREATED,
    Col.DATE,
    Col.CLOSED_AT,
    Col.TAKEN_AT,
)
