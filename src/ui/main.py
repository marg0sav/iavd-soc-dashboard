from pathlib import Path

import pandas as pd
import taipy.gui.builder as tgb
from taipy.gui import Gui

from src.analytics import (
    build_incident_chart as make_chart_figure,
    extract_visible_range,
    calculate_summary_stats,
)
from src.service import IncidentService

from .state import initial_state

from .components.summary import build_summary
from .components.incident_queue import build_incident_queue
from .components.incident_chart import build_incident_chart
from .components.incident_card import build_incident_card


# --------------------------------------
# Начальное состояние Taipy
# --------------------------------------

globals().update(initial_state())

_service: IncidentService | None = None


# --------------------------------------
# Краткая статистика
# --------------------------------------

def update_summary(state, period):
    incidents = _service.repository.get_all()

    result = calculate_summary_stats(
        incidents,
        period=period,
    )

    state.summary_new = result["new"]
    state.summary_critical = result["critical"]
    state.summary_no_verdict = result["no_verdict"]
    state.summary_no_owner = result["no_owner"]


def on_summary_period_change(state, var_name, value):
    update_summary(state, value)


# --------------------------------------
# Очередь инцидентов
# --------------------------------------

def update_queue(state):
    queue = _service.get_queue(
        state.search,
        state.severity,
    )

    state.queue_df = queue
    state.queue_count = len(queue)


def on_filter_change(state, var_name, value):
    update_queue(state)


def on_reset(state, id, payload):
    state.search = ""
    state.severity = "Все"

    update_queue(state)


# --------------------------------------
# Карточка инцидента
# --------------------------------------

def on_row_selected(state, var_name, payload):
    index = payload.get("index")

    if index is None:
        return

    if index not in state.queue_df.index:
        return

    entity_id = state.queue_df.loc[index, "ID"]

    state.card_df = _service.get_card(entity_id)
    state.selected_title = f"Инцидент {entity_id}"
    state.card_open = True


def on_card_close(state, id, payload):
    state.card_open = False


# --------------------------------------
# Динамика инцидентов
# --------------------------------------

def on_stats_period_change(state, var_name, value):
    state.stats_zoom_range = None

    incidents = _service.repository.get_all()

    state.stats_figure = make_chart_figure(
        incidents,
        period=value,
        visible_range=None,
    )


def on_stats_range_change(state, id, payload):
    visible_range = extract_visible_range(payload)

    if visible_range == state.stats_zoom_range:
        return

    state.stats_zoom_range = visible_range

    incidents = _service.repository.get_all()

    state.stats_figure = make_chart_figure(
        incidents,
        period=state.stats_period,
        visible_range=visible_range,
    )


# --------------------------------------
# Инициализация пользовательской сессии
# --------------------------------------

def on_init(state):
    update_queue(state)
    update_summary(state, state.summary_period)


# --------------------------------------
# Построение главной страницы
# --------------------------------------

def build_page():
    with tgb.Page() as page:

        # 1. Краткая статистика
        build_summary(
            on_period_change=on_summary_period_change,
        )

        # 2. Очередь
        build_incident_queue(
            on_filter_change=on_filter_change,
            on_reset=on_reset,
            on_row_selected=on_row_selected,
        )

        # 3. График
        build_incident_chart(
            on_period_change=on_stats_period_change,
            on_range_change=on_stats_range_change,
        )

        # 4. Модальное окно
        build_incident_card(
            on_close=on_card_close,
        )

    return page


# Создаём GUI на уровне модуля, так Taipy использует контекст src.ui.main.

_gui = Gui(
    page=build_page(),
    css_file=str(
        Path(__file__).resolve().parents[2]
        / "styles.css"
    ),
)

_gui.on_init = on_init


# --------------------------------------
# Создание GUI
# --------------------------------------

def create_gui(service: IncidentService) -> Gui:
    global _service
    global queue_df, queue_count, severity_options
    global summary_new, summary_critical
    global summary_no_verdict, summary_no_owner
    global stats_figure

    _service = service

    incidents = service.repository.get_all()

    # Очередь инцидентов
    queue_df = service.get_queue()
    queue_count = len(queue_df)
    severity_options = service.get_severities()

    # Краткая статистика
    summary = calculate_summary_stats(
        incidents,
        period=summary_period,
    )

    summary_new = summary["new"]
    summary_critical = summary["critical"]
    summary_no_verdict = summary["no_verdict"]
    summary_no_owner = summary["no_owner"]

    # Динамика инцидентов
    stats_figure = make_chart_figure(
        incidents,
        period=stats_period,
        visible_range=None,
    )

    return _gui
