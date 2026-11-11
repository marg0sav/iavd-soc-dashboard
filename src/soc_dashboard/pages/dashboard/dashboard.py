from datetime import date, datetime, time

import pandas as pd
import taipy.gui.builder as tgb

from soc_dashboard.analytics import (
    build_dashboard_overview,
    build_incident_chart,
    calculate_summary_comparison,
    extract_visible_range,
)
from soc_dashboard.constants import ALL, NO_DATA
from soc_dashboard.data.data import get_incident_service
from soc_dashboard.domain.columns import Col
from soc_dashboard.domain.period import PERIOD_OPTIONS, Period, period_to_date_range
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

summary_sla_value = NO_DATA
summary_sla_note = "Нет заполненного SLA"

summary_take_value = NO_DATA
summary_take_note = "Нет корректных дат"

types_figure = None
verdicts_figure = None

overview_chart_config = {
    "displayModeBar": False,
    "responsive": True,
}


def preset_period_to_date_range(period: str) -> tuple[date, date]:
    """Диапазон дат записей датасета по выбранному периоду."""

    # NOTE: ВАЖНО!!! Для статического датасета:
    # "сегодня" исчисляется от самой новой записи SOC (MAX по Col.Created);
    #
    # для реально поступающих данных тут скорее должно быть что то типо time.now().
    today = (get_incident_service().repository.get_all()[Col.CREATED].max()).date()

    if period == Period.ALL_TIME:
        # NOTE: Первый день для датасета самая старая (MIN по Col.Created) запись SOC.
        first_day = (
            get_incident_service().repository.get_all()[Col.CREATED].min().date()
        )
        return (first_day, today)

    return period_to_date_range(period, today)


def apply_summary_period(state, period, date_from, date_to):
    """Единая обработка: toggle, date_range и сводка всегда с единым периодом."""
    state.summary_period = period

    state.summary_dates = [
        datetime.combine(date_from, time()),
        datetime.combine(date_to, time()),
    ]

    state.summary_date_error = ""
    update_summary(state, period, date_from, date_to)
    # Очередь и график динамики инцидетнов читают даты из state.summary_dates
    update_queue(state)
    update_chart(state)


def on_apply_summary_range(state):
    date_from, date_to = (
        tgb_date_range_to_date(value) for value in state.summary_dates
    )

    # Вторая дата ещё не выбрана: ждём, а не показываем ошибку
    if date_from is None or date_to is None:
        return

    if date_from > date_to:
        state.summary_date_error = "Дата начала не может быть позже даты окончания"
        return

    apply_summary_period(state, Period.CUSTOM, date_from, date_to)


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

    overview = build_dashboard_overview(
        incidents,
        period=period,
        date_from=date_from,
        date_to=date_to,
    )

    state.summary_sla_value = overview["sla_value"]
    state.summary_sla_note = overview["sla_note"]

    state.summary_take_value = overview["take_value"]
    state.summary_take_note = overview["take_note"]

    state.types_figure = overview["types_figure"]
    state.verdicts_figure = overview["verdicts_figure"]


def on_summary_period_change(state, var_name, value):
    if value == Period.CUSTOM:
        return

    apply_summary_period(state, value, *preset_period_to_date_range(value))


def update_chart(state, visible_range=None):
    """График динамики за выбранный период, visible_range - зум внутри него."""
    date_from, date_to = (
        tgb_date_range_to_date(value) for value in state.summary_dates
    )

    state.stats_zoom_range = visible_range
    state.stats_figure = build_incident_chart(
        get_incident_service().repository.get_all(),
        date_from,
        date_to,
        visible_range=visible_range,
    )


def on_stats_range_change(state, id, payload):
    visible_range = extract_visible_range(payload)

    if visible_range == state.stats_zoom_range:
        return

    update_chart(state, visible_range)


def load_incident(state, entity_id):
    state.card_df = get_incident_service().get_card(entity_id)
    state.selected_title = f"Инцидент {entity_id}"


def update_queue(state):
    date_from, date_to = (
        tgb_date_range_to_date(value) for value in state.summary_dates
    )

    queue = get_incident_service().get_queue(
        state.search,
        state.severity,
        date_from,
        date_to,
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

    # Очередь и график динамики инцидентов обновятся внутри apply_summary_period вместе со сводкой
    apply_summary_period(
        state, state.summary_period, *preset_period_to_date_range(state.summary_period)
    )


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
        with tgb.part(class_name="soc-toolbar soc-summary-controls"):
            tgb.text("## Сводка", mode="md")
            tgb.toggle(
                "{summary_period}",
                lov=summary_period_options,
                on_change=on_summary_period_change,
                class_name="soc-period",
            )
            tgb.date_range(
                "{summary_dates}",
                label_start="С",
                label_end="По",
                format="dd.MM.yyyy",
                on_change=on_apply_summary_range,
            )

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
                    tgb.text(
                        f"{{summary_{key}}}",
                        class_name="metric-value",
                    )
                    tgb.text(
                        f"{{summary_{key}_change}}",
                        class_name="metric-change",
                    )

            with tgb.part(class_name="soc-metric metric-sla"):
                tgb.text(
                    "Нарушения SLA взятия в работу",
                    class_name="metric-label",
                )
                tgb.text(
                    "{summary_sla_value}",
                    class_name="metric-value",
                )
                tgb.text(
                    "{summary_sla_note}",
                    class_name="metric-note",
                )

            with tgb.part(class_name="soc-metric metric-take"):
                tgb.text(
                    "Время до взятия в работу",
                    class_name="metric-label",
                )
                tgb.text(
                    "{summary_take_value}",
                    class_name="metric-value",
                )
                tgb.text(
                    "{summary_take_note}",
                    class_name="metric-note",
                    hover_text="Карточки без даты взятия в работу или без вердитка - не учитываются",
                )

        with tgb.part(class_name="soc-panels"):
            with tgb.part(class_name="soc-panel"):
                with tgb.part(class_name="soc-toolbar"):
                    tgb.text("## Очередь инцидентов", mode="md")
                    tgb.text("Найдено: {queue_count}")

                with tgb.part(class_name="soc-filters"):
                    tgb.input("{search}", label="Поиск", on_change=on_filter_change)
                    tgb.selector(
                        "{severity}",
                        lov="{severity_options}",
                        label="Критичность",
                        dropdown=True,
                        on_change=on_filter_change,
                    )
                    tgb.button("Сбросить фильтры", on_action=on_reset)

                tgb.table(
                    "{queue_df}",
                    on_action=on_row_selected,
                    editable=False,
                    page_size=20,
                    page_size_options=[20],
                    width="100%",
                    height="min(420px, calc(100dvh - 390px))",
                    class_name="soc-queue",
                )

            with tgb.part(class_name="soc-analytics"):
                with tgb.part(class_name="soc-panel"):
                    with tgb.part(class_name="soc-toolbar"):
                        tgb.text(
                            "## Динамика инцидентов",
                            mode="md",
                        )

                    tgb.chart(
                        figure="{stats_figure}",
                        width="100%",
                        height="var(--soc-dynamics-height)",
                        id="incident-stats-chart",
                        on_range_change=on_stats_range_change,
                    )

                with tgb.part(class_name="soc-breakdowns"):
                    with tgb.part(
                        class_name="soc-panel soc-mini-panel",
                    ):
                        tgb.text(
                            "### Топ-5 типов инцидентов",
                            mode="md",
                        )
                        tgb.text(
                            "За период сводки",
                            class_name="soc-panel-note",
                        )
                        tgb.chart(
                            figure="{types_figure}",
                            width="100%",
                            height="var(--soc-breakdown-height)",
                            plot_config="{overview_chart_config}",
                        )

                    with tgb.part(
                        class_name="soc-panel soc-mini-panel",
                    ):
                        tgb.text(
                            "### Распределение вердиктов",
                            mode="md",
                        )
                        tgb.text(
                            "За период сводки",
                            class_name="soc-panel-note",
                        )
                        tgb.chart(
                            figure="{verdicts_figure}",
                            width="100%",
                            height="var(--soc-breakdown-height)",
                            plot_config="{overview_chart_config}",
                        )

    with tgb.dialog(
        "{card_open}",
        title="Карточка инцидента",
        width="850px",
        labels=["Закрыть"],
        on_action=close_card,
    ):
        tgb.text("{selected_title}")
        tgb.table("{card_df}", editable=False, page_size=20, width="100%")
