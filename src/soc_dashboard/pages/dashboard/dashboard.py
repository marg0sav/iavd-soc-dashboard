import pandas as pd
import taipy.gui.builder as tgb

from soc_dashboard.constants import ALL
from soc_dashboard.data.data import get_incident_service
from soc_dashboard.service import QUEUE_COLUMNS, QUEUE_ID, empty_card
from soc_dashboard.analytics import build_incident_chart, extract_visible_range


queue_df = pd.DataFrame(columns=QUEUE_COLUMNS)
card_df = empty_card()

search = ""
severity = ALL
severity_options = [ALL]

selected_title = "Выберите инцидент"
queue_count = 0

stats_period = "30 дней"

stats_period_options = [
    "24 часа",
    "7 дней",
    "30 дней",
    "Год",
    "Весь период",
]

stats_figure = None
stats_zoom_range = None


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


def on_filter_change(state, var_name, value):
    update_queue(state)


def on_row_selected(state, var_name, payload):
    index = payload.get("index")

    if index in state.queue_df.index:
        entity_id = state.queue_df.loc[index, QUEUE_ID]
        load_incident(state, entity_id)


def on_reset(state):
    state.search = ""
    state.severity = ALL
    update_queue(state)


with tgb.Page() as dashboard_page:
    tgb.text(
        "# Очередь инцидентов SOC",
        mode="md",)


    with tgb.part(class_name="panel"):
        tgb.text("## Динамика новых инцидентов", mode="md")

        tgb.toggle(
            "{stats_period}",
            lov="{stats_period_options}",
            on_change=on_stats_period_change,
            class_name="stats-period-toggle",
        )

        tgb.chart(
            figure="{stats_figure}",
            width="100%",
            id="incident-stats-chart",
            on_range_change=on_stats_range_change,
        )

    with tgb.part(class_name="panel"):
        tgb.input(
            "{search}",
            label="Поиск",
            on_change=on_filter_change,
        )

        tgb.selector(
            "{severity}",
            lov="{severity_options}",
            label="Критичность",
            dropdown=True,
            on_change=on_filter_change,
        )

        tgb.button(
            "Сбросить фильтры",
            on_action=on_reset,
        )

        tgb.text("Найдено: {queue_count}")

        tgb.table(
            "{queue_df}",
            on_action=on_row_selected,
            editable=False,
            page_size=10,
            width="100%",
        )

    with tgb.part(class_name="panel"):
        tgb.text(
            "## Карточка инцидента",
            mode="md",
        )

        tgb.text("{selected_title}")

        tgb.table(
            "{card_df}",
            editable=False,
            page_size=20,
            width="100%",
        )
