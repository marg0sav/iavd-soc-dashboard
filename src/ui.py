import re
from datetime import datetime
from pathlib import Path
import pandas as pd
import taipy.gui.builder as tgb
from taipy.gui import Gui

from src.constants import ALL
from src.service import IncidentService, QUEUE_COLUMNS, QUEUE_ID, empty_card
from src.analytics import build_incident_chart, extract_visible_range, calculate_summary_comparison


queue_df = pd.DataFrame(columns=QUEUE_COLUMNS)
card_df = empty_card()

search = ""
severity = ALL
severity_options = [ALL]

selected_title = "Выберите инцидент"
queue_count = 0

# -----------------------------------------
# Временные периоды
# -----------------------------------------

PERIOD_OPTIONS = [
    "24 часа",
    "7 дней",
    "30 дней",
    "Год",
    "Весь период",
]

stats_period = "30 дней"
summary_period = "24 часа"

summary_period_options = PERIOD_OPTIONS + ["Свой период"]

summary_date_from = ""
summary_date_to = ""

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

summary_new_change = "—"
summary_critical_change = "—"
summary_no_verdict_change = "—"
summary_no_owner_change = "—"

_service: IncidentService | None = None

def format_date_input(value):
    text = str(value or "").strip()

    # Разрешаем только цифры и точки
    if not re.fullmatch(r"[0-9.]*", text):
        raise ValueError("Разрешены только цифры и точки")

    digits = text.replace(".", "")[:8]

    parts = [
        digits[:2],
        digits[2:4],
        digits[4:8],
    ]

    return ".".join(part for part in parts if part)


def parse_date_input(value):
    if not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", value):
        raise ValueError(
            "Введите дату полностью: ДД.ММ.ГГГГ"
        )

    try:
        return datetime.strptime(value, "%d.%m.%Y").date()
    except ValueError:
        raise ValueError("Указана несуществующая дата")

def on_apply_summary_range(state):
    try:
        date_from = parse_date_input(state.summary_date_from)
        date_to = parse_date_input(state.summary_date_to)

        if date_from > date_to:
            raise ValueError(
                "Дата начала не может быть позже даты окончания"
            )

        if _service is None:
            raise ValueError("Данные ещё не загружены")

        incidents = _service.repository.get_all()

        result = calculate_summary_comparison(
            incidents,
            period="Свой период",
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

        state.summary_period = "Свой период"
        state.summary_date_error = ""

    except ValueError as exc:
        state.summary_date_error = str(exc)

def update_summary(state, period):
    incidents = _service.repository.get_all()

    result = calculate_summary_comparison(
        incidents,
        period=period,
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
    if value == "Свой период":
        on_apply_summary_range(state)
        return

    state.summary_date_error = ""
    update_summary(state, value)

def on_summary_date_change(state, var_name, value):
    try:
        formatted = format_date_input(value)
        setattr(state, var_name, formatted)
        state.summary_date_error = ""
    except ValueError as exc:
        state.summary_date_error = str(exc)

def on_stats_period_change(state, var_name, value):
    incidents = _service.repository.get_all()

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

    incidents = _service.repository.get_all()

    state.stats_figure = build_incident_chart(
        incidents,
        period=state.stats_period,
        visible_range=visible_range,
    )

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
        state.card_df = empty_card()
        state.selected_title = "Инциденты не найдены"
    else:
        load_incident(
            state,
            queue.iloc[0][QUEUE_ID],
        )


def on_init(state):
    update_queue(state)
    update_summary(state, state.summary_period)


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


def build_page():
    with tgb.Page() as page:
        
        with tgb.part(class_name="panel"):
            tgb.text("## Динамика новых инцидентов", mode="md")

            tgb.toggle(
                "{stats_period}",
                lov=PERIOD_OPTIONS,
                on_change=on_stats_period_change,
                class_name="stats-period-toggle",
            )

            tgb.chart(
                figure="{stats_figure}",
                width="100%",
                id="incident-stats-chart",
                on_range_change=on_stats_range_change,
            )

        with tgb.part(class_name="summary-section"):

            with tgb.layout(
                columns="auto 140px 140px auto",
                class_name="summary-controls",
            ):
                tgb.toggle(
                    "{summary_period}",
                    lov=summary_period_options,
                    on_change=on_summary_period_change,
                    class_name="summary-period-toggle",
                )

                tgb.input(
                    "{summary_date_from}",
                    label="С",
                    on_change=on_summary_date_change,
                    change_delay=500,
                    class_name="summary-date-input",
                )

                tgb.input(
                    "{summary_date_to}",
                    label="По",
                    on_change=on_summary_date_change,
                    change_delay=500,
                    class_name="summary-date-input",
                )

                tgb.button(
                    "Применить",
                    on_action=on_apply_summary_range,
                    class_name="summary-apply-button",
                )

            tgb.text(
                "{summary_date_error}",
                class_name="summary-date-error",
            )

            with tgb.layout(
                columns="1 1 1 1",
                class_name="summary-grid",
            ):

                with tgb.part(class_name="summary-card"):
                    tgb.text(
                        "Новые инциденты",
                        class_name="summary-label",
                    )
                    tgb.text(
                        "{summary_new}  {summary_new_change}",
                        class_name="summary-metric-line",
                    )

                with tgb.part(class_name="summary-card"):
                    tgb.text(
                        "Критические инциденты",
                        class_name="summary-label",
                    )
                    tgb.text(
                        "{summary_critical}  {summary_critical_change}",
                        class_name="summary-metric-line critical-metric",
                    )

                with tgb.part(class_name="summary-card"):
                    tgb.text(
                        "Без вердикта",
                        class_name="summary-label",
                    )
                    tgb.text(
                        "{summary_no_verdict}  {summary_no_verdict_change}",
                        class_name="summary-metric-line",
                    )

                with tgb.part(class_name="summary-card"):
                    tgb.text(
                        "Без ответственного",
                        class_name="summary-label",
                    )
                    tgb.text(
                        "{summary_no_owner}  {summary_no_owner_change}",
                        class_name="summary-metric-line",
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
    global _service, queue_df, severity_options
    global queue_count, stats_figure

    global summary_new, summary_critical
    global summary_no_verdict, summary_no_owner

    global summary_new_change, summary_critical_change
    global summary_no_verdict_change, summary_no_owner_change

    _service = service
    incidents = service.repository.get_all()

    # Очередь инцидентов
    queue_df = service.get_queue()
    queue_count = len(queue_df)
    severity_options = service.get_severities()

    # Краткая статистика
    result = calculate_summary_comparison(
        incidents,
        period=summary_period,
    )

    current = result["current"]
    changes = result["changes"]

    summary_new = current["new"]
    summary_critical = current["critical"]
    summary_no_verdict = current["no_verdict"]
    summary_no_owner = current["no_owner"]

    summary_new_change = changes["new"]
    summary_critical_change = changes["critical"]
    summary_no_verdict_change = changes["no_verdict"]
    summary_no_owner_change = changes["no_owner"]

    # Динамика инцидентов
    stats_figure = build_incident_chart(
        service.repository.get_all(),
        period=stats_period,
        visible_range=None,
    )

    return _gui
  
_gui = Gui(
    page=build_page(),
    css_file=str(
        Path(__file__).resolve().parents[1] / "styles.css"
    ),
)

_gui.on_init = on_init
