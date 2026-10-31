from datetime import datetime, time, timedelta

import pandas as pd
import taipy.gui.builder as tgb

from soc_dashboard.analytics import (
    build_incident_chart,
    calculate_summary_comparison,
    extract_visible_range,
)
from soc_dashboard.constants import ALL, NO_DATA
from soc_dashboard.data.data import get_incident_service
from soc_dashboard.domain.columns import Col
from soc_dashboard.domain.period import PERIOD_OPTIONS, Period
from soc_dashboard.pages.dashboard.utils import tgb_date_range_to_date
from soc_dashboard.service import QUEUE_COLUMNS, QUEUE_ID, empty_card

queue_df = pd.DataFrame(columns=QUEUE_COLUMNS)
card_df = empty_card()

queue_df = pd.DataFrame(columns=QUEUE_COLUMNS)
card_df = empty_card()
card_open = False

search = ""
severity = ALL
severity_options = [ALL]

selected_title = "Выберите инцидент"
queue_count = 0

# -----------------------------------------
# Временные периоды
# -----------------------------------------

stats_period = "30 дней"
summary_period = Period.DAY

summary_period_options = PERIOD_OPTIONS + [Period.CUSTOM]

# Границы своего периода [начало, конец], задаются в on_init
summary_dates = [None, None]

summary_date_error = ""

stats_figure = None
stats_zoom_range = None

# -----------------------------------------
# Краткая статистика
# -----------------------------------------

summary_new = 0
summary_critical = 0
summary_no_verdict = 0
summary_no_owner = 0

summary_new_change = NO_DATA
summary_critical_change = NO_DATA
summary_no_verdict_change = NO_DATA
summary_no_owner_change = NO_DATA


def default_summary_dates():
    """Последние 30 дней датасета."""
    latest = get_incident_service().repository.get_all()[Col.CREATED].max().date()

    # Полночь без часового пояса: браузер покажет тот же день в любом поясе
    return [
        datetime.combine(latest - timedelta(days=29), time()),
        datetime.combine(latest, time()),
    ]


def on_apply_summary_range(state):
    date_from, date_to = (
        tgb_date_range_to_date(value) for value in state.summary_dates
    )

    if date_from is None or date_to is None:
        state.summary_date_error = "Выберите дату начала и окончания"
        return

    if date_from > date_to:
        state.summary_date_error = "Дата начала не может быть позже даты окончания"
        return

    update_summary(state, Period.CUSTOM, date_from, date_to)

    state.summary_period = Period.CUSTOM
    state.summary_date_error = ""


def update_summary(state, period, date_from, date_to):
    incidents = get_incident_service().repository.get_all()

    result = calculate_summary_comparison(
        incidents,
        period=period,
        date_from=date_from,
        date_to=date_to,
    )

    current = result["current"]
    changes = result["changes"]

    state.summary_new = current["new"]
    state.summary_critical = current["critical"]
    state.summary_no_verdict = current["no_verdict"]
    state.summary_no_owner = current["no_owner"]

    state.summary_new_change = changes["new"]
    state.summary_critical_change = changes["critical"]
    state.summary_no_verdict_change = changes["no_verdict"]
    state.summary_no_owner_change = changes["no_owner"]


def on_summary_period_change(state, var_name, value):
    if value == Period.CUSTOM:
        on_apply_summary_range(state)
        return

    state.summary_date_error = ""
    update_summary(state, value, None, None)


def on_stats_period_change(state, var_name, value):
    incidents = get_incident_service().repository.get_all()

    state.stats_zoom_range = None
    state.stats_figure = build_incident_chart(
        incidents,
        period=value,
        visible_range=None,
    )


def on_stats_range_change(state, id, payload):
    visible_range = extract_visible_range(payload)

    if visible_range == state.stats_zoom_range:
        return

    state.stats_zoom_range = visible_range

    incidents = get_incident_service().repository.get_all()

    state.stats_figure = build_incident_chart(
        incidents,
        period=state.stats_period,
        visible_range=visible_range,
    )


def load_incident(state, entity_id):
    state.card_df = get_incident_service().get_card(entity_id)
    state.selected_title = f"Инцидент {entity_id}"


def update_queue(state):
    queue = get_incident_service().get_queue(
        state.search,
        state.severity,
    )

    state.queue_df = queue
    state.queue_count = len(queue)

    if queue.empty:
        state.card_df = empty_card()
        state.selected_title = "Инциденты не найдены"
    else:
        load_incident(
            state,
            queue.iloc[0][QUEUE_ID],
        )


def on_init(state):
    state.severity_options = get_incident_service().get_severities()
    state.stats_figure = build_incident_chart(
        get_incident_service().repository.get_all(),
        period=state.stats_period,
        visible_range=None,
    )

    update_queue(state)

    state.summary_dates = default_summary_dates()
    update_summary(state, state.summary_period, None, None)


def on_filter_change(state, var_name, value):
    update_queue(state)


def on_row_selected(state, var_name, payload):
    index = payload.get("index")

    if index in state.queue_df.index:
        entity_id = state.queue_df.loc[index, QUEUE_ID]
        load_incident(state, entity_id)
        state.card_open = True

def close_card(state):
    state.card_open = False

def on_reset(state):
    state.search = ""
    state.severity = ALL
    update_queue(state)


with tgb.Page() as dashboard_page:
    with tgb.part(class_name="soc-dashboard"):
        with tgb.part(class_name="soc-toolbar"):
            tgb.text("## Сводка", mode="md")
            tgb.toggle(
                "{summary_period}", lov=summary_period_options,
                on_change=on_summary_period_change, class_name="soc-period",
            )
            tgb.date_range(
                "{summary_dates}", label_start="С", label_end="По", format="dd.MM.yyyy",
            )
            tgb.button("Применить", on_action=on_apply_summary_range)

        with tgb.part(render="{bool(summary_date_error)}"):
            tgb.text("{summary_date_error}")

        with tgb.part(class_name="soc-metrics"):
            for label, key in (
                ("Новые инциденты", "new"),
                ("Критические инциденты", "critical"),
                ("Без вердикта", "no_verdict"),
                ("Без ответственного", "no_owner"),
            ):
                with tgb.part(class_name=f"soc-metric metric-{key}"):
                    tgb.text(label, class_name="metric-label")
                    tgb.text(f"{{summary_{key}}}", class_name="metric-value")
                    tgb.text(f"{{summary_{key}_change}}", class_name="metric-change")

        with tgb.part(class_name="soc-panels"):
            with tgb.part(class_name="soc-panel"):
                with tgb.part(class_name="soc-toolbar"):
                    tgb.text("## Очередь инцидентов", mode="md")
                    tgb.text("Найдено: {queue_count}")

                with tgb.part(class_name="soc-filters"):
                    tgb.input("{search}", label="Поиск", on_change=on_filter_change)
                    tgb.selector(
                        "{severity}", lov="{severity_options}", label="Критичность",
                        dropdown=True, on_change=on_filter_change,
                    )
                    tgb.button("Сбросить фильтры", on_action=on_reset)

                tgb.table(
                    "{queue_df}", on_action=on_row_selected, editable=False,
                    page_size=5, page_size_options=[5],
                    width="100%", height="calc(var(--plot-height) - 116px)",
                    class_name="soc-queue",
                )

            with tgb.part(class_name="soc-panel"):
                with tgb.part(class_name="soc-toolbar"):
                    tgb.text("## Динамика инцидентов", mode="md")
                    tgb.toggle(
                        "{stats_period}", lov=PERIOD_OPTIONS,
                        on_change=on_stats_period_change, class_name="soc-period",
                    )

                tgb.chart(
                    figure="{stats_figure}", width="100%", height="var(--plot-height)",
                    id="incident-stats-chart", on_range_change=on_stats_range_change,
                )

    with tgb.dialog(
        "{card_open}", title="Карточка инцидента", width="850px",
        labels=["Закрыть"], on_action=close_card,
    ):
        tgb.text("{selected_title}")
        tgb.table("{card_df}", editable=False, page_size=20, width="100%")