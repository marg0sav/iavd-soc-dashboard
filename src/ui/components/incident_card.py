import taipy.gui.builder as tgb


def build_incident_card(on_close):
    with tgb.dialog(
        "{card_open}",
        on_action=on_close,
        width="850px",
    ):

        tgb.text(
            "## {selected_title}",
            mode="md",
        )

        tgb.table(
            "{card_df}",
            editable=False,
            page_size=20,
            width="100%",
        )
