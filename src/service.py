import pandas as pd
from src.repository import IncidentRepository

# Порядок критичности для сортировки очереди
# чем меньше число, тем раньше инцидент отображается
SEVERITY_ORDER = {
    "критическая": 0,
    "critical": 0,
    "высокая": 1,
    "high": 1,
    "средняя": 2,
    "medium": 2,
    "низкая": 3,
    "low": 3,
    "информационная": 4,
    "informational": 4,
}

# Названия и порядок столбцов таблицы очереди
QUEUE_COLUMNS = [
    "ID",
    "Создан (UTC)",
    "Тип инцидента",
    "Критичность",
    "Вердикт",
    "Ответственный",
]


def format_value(value) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return "—"

    if isinstance(value, pd.Timestamp):
        return value.strftime("%d.%m.%Y %H:%M UTC")

    return str(value)

class IncidentService:
    def __init__(self, repository: IncidentRepository):
        self.repository = repository

    def get_queue(
        self,
        search: str = "",
        severity: str = "Все",
    ) -> pd.DataFrame:
        df = self.repository.get_all()

        for column in QUEUE_COLUMNS[2:]:
            if column not in df.columns:
                df[column] = pd.NA

        if "Создан" not in df.columns:
            df["Создан"] = pd.NaT

        df["_priority"] = (
            df["Критичность"]
            .astype("string")
            .str.strip()
            .str.casefold()
            .map(SEVERITY_ORDER)
            .fillna(99)
        )

        df = df.sort_values(
            ["_priority", "Создан"],
            kind="stable",
            na_position="last",
        )

        result = pd.DataFrame(index=df.index)

        result["ID"] = df["EntityId"]
        result["Создан (UTC)"] = df["Создан"].map(format_value)

        for column in QUEUE_COLUMNS[2:]:
            result[column] = df[column].map(format_value)

        if severity != "Все":
            result = result[
                result["Критичность"] == severity
            ]

        if search.strip():
            mask = result.apply(
                lambda column: column.astype(str).str.contains(
                    search.strip(),
                    case=False,
                    regex=False,
                    na=False,
                )
            ).any(axis=1)

            result = result[mask]

        return result.reset_index(drop=True)

    def get_severities(self) -> list[str]:
        values = (
            self.get_queue()["Критичность"]
            .drop_duplicates()
            .tolist()
        )

        return ["Все", *values]

    def get_incident(self, entity_id: str) -> dict | None:
        return self.repository.get_by_id(entity_id)

    def get_card(self, entity_id: str) -> pd.DataFrame:
        incident = self.get_incident(entity_id)

        if incident is None:
            return pd.DataFrame(
                columns=["Поле", "Значение"]
            )

        rows = [
            {
                "Поле": key,
                "Значение": format_value(value),
            }
            for key, value in incident.items()
        ]

        return pd.DataFrame(
            rows,
            columns=["Поле", "Значение"],
        )
