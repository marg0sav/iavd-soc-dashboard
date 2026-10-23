import taipy.gui.builder as tgb


def build_incident_queue(
    on_filter_change,
    on_reset,
    on_row_selected,
):
    with tgb.part(class_name="panel"):

        tgb.text(
            "## Очередь инцидентов",
            mode="md",
        )

        with tgb.layout(columns="2 1 1"):

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
