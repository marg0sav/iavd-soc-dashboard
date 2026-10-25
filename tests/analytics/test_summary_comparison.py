from dataclasses import dataclass

import pandas as pd
import pytest

from soc_dashboard.analytics import calculate_summary_comparison
from soc_dashboard.constants import NO_DATA, Col, Period


@dataclass(kw_only=True)
class Case:
    """Входные данные calculate_summary_comparison и ожидаемый результат."""

    # Имя случая в отчёте pytest
    id: str

    # Инциденты: одна строка - один инцидент со столбцами
    # (Col.CREATED, Col.SEVERITY, Col.VERDICT, Col.ASSIGNEE).
    # None в вердикте или ответственном - значение не заполнено.
    rows: list[tuple]

    # Аргументы calculate_summary_comparison
    period: str
    # Границы своего периода, обе включительно, "ГГГГ-ММ-ДД".
    # None - свой период не задан, границы считаются по period.
    # Свой период применяется, только если заданы обе даты.
    date_from: str | None
    date_to: str | None

    # Ожидаемые result["current"] и result["changes"] целиком
    current: dict
    changes: dict


CASES = [
    Case(
        id="custom_range_metrics",
        rows=[
            ("2024-01-10 10:00", "Критическая", "Ложное срабатывание", "Иванов"),
            ("2024-01-11 12:00", "high", "", "не указан"),
            ("2024-01-11 13:00", "low", None, None),
        ],
        period=Period.CUSTOM,
        date_from="2024-01-10",
        date_to="2024-01-11",
        current={"new": 3, "critical": 1, "no_verdict": 2, "no_owner": 2},
        changes={
            "new": NO_DATA,
            "critical": NO_DATA,
            "no_verdict": NO_DATA,
            "no_owner": NO_DATA,
        },
    ),
    Case(
        id="custom_range_includes_whole_last_day",
        rows=[
            ("2024-01-11 23:59", "low", "Инцидент", "Иванов"),
            ("2024-01-12 00:00", "low", "Инцидент", "Иванов"),
        ],
        period=Period.CUSTOM,
        date_from="2024-01-10",
        date_to="2024-01-11",
        current={"new": 1, "critical": 0, "no_verdict": 0, "no_owner": 0},
        changes={
            "new": NO_DATA,
            "critical": NO_DATA,
            "no_verdict": NO_DATA,
            "no_owner": NO_DATA,
        },
    ),
    Case(
        id="changes_vs_previous_period_of_same_length",
        rows=[
            # Предыдущий период: 08.01-09.01
            ("2024-01-08 10:00", "critical", "Инцидент", "Иванов"),
            ("2024-01-08 11:00", "low", "Инцидент", "Иванов"),
            ("2024-01-09 10:00", "low", "Инцидент", "Иванов"),
            ("2024-01-09 11:00", "low", "Инцидент", "Иванов"),
            # Текущий период: 10.01-11.01
            ("2024-01-10 10:00", "critical", "", "Иванов"),
            ("2024-01-11 10:00", "low", "Инцидент", "Иванов"),
        ],
        period=Period.CUSTOM,
        date_from="2024-01-10",
        date_to="2024-01-11",
        current={"new": 2, "critical": 1, "no_verdict": 1, "no_owner": 0},
        # Без вердикта и без ответственного в предыдущем периоде 0:
        # процент не определён.
        changes={
            "new": "↓ 50%",
            "critical": "→ 0%",
            "no_verdict": NO_DATA,
            "no_owner": NO_DATA,
        },
    ),
    Case(
        id="period_counts_back_from_latest_incident",
        rows=[
            # Предыдущие 24 часа
            ("2024-01-09 11:59", "low", "Инцидент", "Иванов"),
            # Последние 24 часа от последнего инцидента, граница включена
            ("2024-01-09 12:00", "low", "Инцидент", "Иванов"),
            ("2024-01-10 12:00", "low", "Инцидент", "Иванов"),
        ],
        period=Period.DAY,
        date_from=None,
        date_to=None,
        current={"new": 2, "critical": 0, "no_verdict": 0, "no_owner": 0},
        changes={
            "new": "↑ 100%",
            "critical": NO_DATA,
            "no_verdict": NO_DATA,
            "no_owner": NO_DATA,
        },
    ),
    Case(
        id="all_time_has_no_changes",
        rows=[
            ("2023-01-01 10:00", "low", "Инцидент", "Иванов"),
            ("2024-01-10 10:00", "low", "Инцидент", "Иванов"),
        ],
        date_from=None,
        date_to=None,
        period=Period.ALL_TIME,
        current={"new": 2, "critical": 0, "no_verdict": 0, "no_owner": 0},
        changes={
            "new": NO_DATA,
            "critical": NO_DATA,
            "no_verdict": NO_DATA,
            "no_owner": NO_DATA,
        },
    ),
    Case(
        id="empty_incidents",
        rows=[],
        period=Period.DAY,
        date_from=None,
        date_to=None,
        current={"new": 0, "critical": 0, "no_verdict": 0, "no_owner": 0},
        changes={
            "new": NO_DATA,
            "critical": NO_DATA,
            "no_verdict": NO_DATA,
            "no_owner": NO_DATA,
        },
    ),
]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.id)
def test_summary_comparison(case):
    incidents = pd.DataFrame(
        case.rows,
        columns=[Col.CREATED, Col.SEVERITY, Col.VERDICT, Col.ASSIGNEE],
    )

    result = calculate_summary_comparison(
        incidents,
        period=case.period,
        date_from=case.date_from,
        date_to=case.date_to,
    )

    assert result == {"current": case.current, "changes": case.changes}
