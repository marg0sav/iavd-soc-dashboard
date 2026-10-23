import taipy.gui.builder as tgb


def build_summary(on_period_change):
    with tgb.part(class_name="summary-section"):

        tgb.toggle(
            "{summary_period}",
            lov="{summary_period_options}",
            on_change=on_period_change,
            class_name="summary-period-toggle",
        )

        with tgb.layout(
            columns="1 1 1 1",
            class_name="summary-grid",
        ):

            with tgb.part(class_name="card summary-card"):
                tgb.text(
                    "Новые инциденты",
                    class_name="summary-label",
                )
                tgb.text(
                    "{summary_new}  {summary_new_change}",
                    class_name="summary-metric-line",
                )

            with tgb.part(class_name="card summary-card"):
                tgb.text(
                    "Критические инциденты",
                    class_name="summary-label",
                )
                tgb.text(
                    "{summary_critical}  {summary_critical_change}",
                    class_name="summary-metric-line critical-metric",
                )

            with tgb.part(class_name="card summary-card"):
                tgb.text(
                    "Без вердикта",
                    class_name="summary-label",
                )
                tgb.text(
                    "{summary_no_verdict}  {summary_no_verdict_change}",
                    class_name="summary-metric-line",
                )

            with tgb.part(class_name="card summary-card"):
                tgb.text(
                    "Без ответственного",
                    class_name="summary-label",
                )
                tgb.text(
                    "{summary_no_owner}  {summary_no_owner_change}",
                    class_name="summary-metric-line",
                )
