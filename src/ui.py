from pathlib import Path
import pandas as pd
import taipy.gui.builder as tgb
from taipy.gui import Gui

from src.service import IncidentService, QUEUE_COLUMNS


queue_df = pd.DataFrame(columns=QUEUE_COLUMNS)
card_df = pd.DataFrame(columns=["Поле", "Значение"])

search = ""
severity = "Все"
severity_options = ["Все"]

selected_title = "Выберите инцидент"
queue_count = 0

_service: IncidentService | None = None


def load_incident(state, entity_id):
    state.card_df = _service.get_card(entity_id)
    state.selected_title = f"Инцидент {entity_id}"


def update_queue(state):
    queue = _service.get_queue(
        state.search,
        state.severity,
    )

    state.queue_df = queue
    state.queue_count = len(queue)

    if queue.empty:
        state.card_df = pd.DataFrame(
            columns=["Поле", "Значение"]
        )
        state.selected_title = "Инциденты не найдены"
    else:
        load_incident(
            state,
            queue.iloc[0]["ID"],
        )


def on_init(state):
    update_queue(state)


def on_filter_change(state, var_name, value):
    update_queue(state)


def on_row_selected(state, var_name, payload):
    index = payload.get("index")

    if index in state.queue_df.index:
        entity_id = state.queue_df.loc[index, "ID"]
        load_incident(state, entity_id)


def on_reset(state):
    state.search = ""
    state.severity = "Все"
    update_queue(state)


def build_page():
    with tgb.Page() as page:
        tgb.text(
            "# Очередь инцидентов SOC",
            mode="md",
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

    return page


def create_gui(service: IncidentService) -> Gui:
    global _service, queue_df, severity_options, queue_count

    _service = service
    queue_df = service.get_queue()
    queue_count = len(queue_df)
    severity_options = service.get_severities()

    return _gui
  
_gui = Gui(
    page=build_page(),
    css_file=str(
        Path(__file__).resolve().parents[1] / "styles.css"
    ),
)

_gui.on_init = on_init
