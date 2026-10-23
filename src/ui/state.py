import pandas as pd

from src.service import QUEUE_COLUMNS


PERIOD_OPTIONS = [
    "24 часа",
    "7 дней",
    "30 дней",
    "Год",
    "Весь период",
]


def initial_state():
    return {
        # Краткая статистика
        "summary_period": "24 часа",
        "summary_period_options": PERIOD_OPTIONS.copy(),
        "summary_new": 0,
        "summary_critical": 0,
        "summary_no_verdict": 0,
        "summary_no_owner": 0,

        # Изменения относительно предыдущего периода
        "summary_new_change": "—",
        "summary_critical_change": "—",
        "summary_no_verdict_change": "—",
        "summary_no_owner_change": "—",

        # Очередь
        "queue_df": pd.DataFrame(columns=QUEUE_COLUMNS),
        "queue_count": 0,
        "search": "",
        "severity": "Все",
        "severity_options": ["Все"],

        # График
        "stats_period": "30 дней",
        "stats_period_options": PERIOD_OPTIONS.copy(),
        "stats_figure": None,
        "stats_zoom_range": None,

        # Карточка инцидента
        "card_df": pd.DataFrame(
            columns=["Поле", "Значение"]
        ),
        "selected_title": "Инцидент",
        "card_open": False,
    }
