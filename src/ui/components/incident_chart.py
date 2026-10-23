import taipy.gui.builder as tgb


def build_incident_chart(
    on_period_change,
    on_range_change,
):
    with tgb.part(class_name="panel"):
        tgb.text(
            "## Динамика новых инцидентов",
            mode="md",
        )

        tgb.toggle(
            "{stats_period}",
            lov="{stats_period_options}",
            on_change=on_period_change,
            class_name="stats-period-toggle",
        )

        tgb.chart(
            figure="{stats_figure}",
            width="100%",
            id="incident-stats-chart",
            on_range_change=on_range_change,
        )