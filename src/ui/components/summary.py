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

            with tgb.part(class_name="summary-card"):
                tgb.text("Новые инциденты")
                tgb.text(
                    "{summary_new}",
                    class_name="summary-value",
                )
                tgb.text(
                    "За выбранный период",
                    class_name="summary-note",
                )

            with tgb.part(class_name="summary-card"):
                tgb.text("Критические инциденты")
                tgb.text(
                    "{summary_critical}",
                    class_name="summary-value critical-value",
                )
                tgb.text(
                    "За выбранный период",
                    class_name="summary-note",
                )

            with tgb.part(class_name="summary-card"):
                tgb.text("Без вердикта")
                tgb.text(
                    "{summary_no_verdict}",
                    class_name="summary-value",
                )
                tgb.text(
                    "За выбранный период",
                    class_name="summary-note",
                )

            with tgb.part(class_name="summary-card"):
                tgb.text("Без ответственного")
                tgb.text(
                    "{summary_no_owner}",
                    class_name="summary-value",
                )
                tgb.text(
                    "За выбранный период",
                    class_name="summary-note",
                )
