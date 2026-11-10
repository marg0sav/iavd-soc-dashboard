from datetime import date

import pandas as pd
import pytest

from soc_dashboard.domain.columns import Col
from soc_dashboard.service import QUEUE_ID, IncidentService


class FakeRepository:
    """Вместо IncidentRepository: отдаёт готовый DataFrame без чтения файла."""

    def __init__(self, df: pd.DataFrame):
        self._df = df

    def get_all(self) -> pd.DataFrame:
        return self._df.copy()


# Инциденты: (ID, время создания в UTC)
INCIDENTS = [
    ("before", "2025-11-13 23:59"),
    ("first_day", "2025-11-14 00:00"),
    ("last_day", "2025-11-20 23:59"),
    ("after", "2025-11-21 00:00"),
]


@pytest.fixture
def service() -> IncidentService:
    df = pd.DataFrame(INCIDENTS, columns=[Col.ID, Col.CREATED])
    df[Col.CREATED] = pd.to_datetime(df[Col.CREATED], utc=True)
    df[Col.SEVERITY] = "Высокая"

    return IncidentService(FakeRepository(df))


@pytest.mark.parametrize(
    ("date_from", "date_to", "expected"),
    [
        # Обе границы включаются целиком
        pytest.param(
            date(2025, 11, 14),
            date(2025, 11, 20),
            {"first_day", "last_day"},
            id="period",
        ),
        # Период не задан - вся очередь
        pytest.param(
            None, None, {"before", "first_day", "last_day", "after"}, id="all"
        ),
        # Задана одна дата - фильтр не применяется
        pytest.param(
            date(2025, 11, 14),
            None,
            {"before", "first_day", "last_day", "after"},
            id="one_date",
        ),
    ],
)
def test_get_queue_filters_by_period(service, date_from, date_to, expected):
    queue = service.get_queue(date_from=date_from, date_to=date_to)

    assert set(queue[QUEUE_ID]) == expected
