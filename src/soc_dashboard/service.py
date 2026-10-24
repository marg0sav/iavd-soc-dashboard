import pandas as pd
from soc_dashboard.constants import ALL, CARD_COLUMNS, CARD_FIELD, CARD_VALUE, Col
from soc_dashboard.repository import IncidentRepository
from soc_dashboard.severity import parse_severity

QUEUE_ID = "ID"
QUEUE_CREATED = "Создан (UTC)"

# Столбцы датасета, которые попадают в очередь как есть
QUEUE_PASSTHROUGH_COLUMNS = [
    Col.INCIDENT_TYPE,
    Col.SEVERITY,
    Col.VERDICT,
    Col.ASSIGNEE,
]

# Названия и порядок столбцов таблицы очереди
QUEUE_COLUMNS = [
    QUEUE_ID,
    QUEUE_CREATED,
    *QUEUE_PASSTHROUGH_COLUMNS,
]


def format_value(value) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return "—"

    if isinstance(value, pd.Timestamp):
        return value.strftime("%d.%m.%Y %H:%M UTC")

    return str(value)


def empty_card() -> pd.DataFrame:
    return pd.DataFrame(columns=CARD_COLUMNS)

class IncidentService:
    def __init__(self, repository: IncidentRepository):
        self.repository = repository

    def get_queue(
        self,
        search: str = "",
        severity: str = ALL,
    ) -> pd.DataFrame:
        df = self.repository.get_all()

        for column in QUEUE_PASSTHROUGH_COLUMNS:
            if column not in df.columns:
                df[column] = pd.NA

        if Col.CREATED not in df.columns:
            df[Col.CREATED] = pd.NaT

        df["_priority"] = (
            parse_severity(df[Col.SEVERITY])
            .map(lambda s: s.priority, na_action="ignore")
            .fillna(99)
        )

        df = df.sort_values(
            ["_priority", Col.CREATED],
            kind="stable",
            na_position="last",
        )

        result = pd.DataFrame(index=df.index)

        result[QUEUE_ID] = df[Col.ID]
        result[QUEUE_CREATED] = df[Col.CREATED].map(format_value)

        for column in QUEUE_PASSTHROUGH_COLUMNS:
            result[column] = df[column].map(format_value)

        if severity != ALL:
            result = result[
                result[Col.SEVERITY] == severity
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
            self.get_queue()[Col.SEVERITY]
            .drop_duplicates()
            .tolist()
        )

        return [ALL, *values]

    def get_incident(self, entity_id: str) -> dict | None:
        return self.repository.get_by_id(entity_id)

    def get_card(self, entity_id: str) -> pd.DataFrame:
        incident = self.get_incident(entity_id)

        if incident is None:
            return empty_card()

        rows = [
            {
                CARD_FIELD: key,
                CARD_VALUE: format_value(value),
            }
            for key, value in incident.items()
        ]

        return pd.DataFrame(
            rows,
            columns=CARD_COLUMNS,
        )
