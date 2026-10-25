from taipy.gui import Gui

from soc_dashboard.pages.dashboard import dashboard
from soc_dashboard.pages.root import root_page

# После "/" (root_page) Taipy показывает страницу после нее [1]
# [1] https://github.com/Avaiga/taipy/blob/5bcb5749521f9ddcc725c009aca00a88ff724e87/frontend/taipy-gui/src/components/Router.tsx#L274-L278
pages = {
    "/": root_page,
    "dashboard": dashboard.dashboard_page,
}


def on_init(state):
    # Глобальный on_init: делегирует инициализацию сессии страницам.
    dashboard.on_init(state)


def main():
    gui = Gui(
        pages=pages,
        css_file="assets/styles.css",
    )

    gui.on_init = on_init

    gui.run(
        title="SOC Dashboard",
        dark_mode=False,
        host="127.0.0.1",
        port=5000,
    )


if __name__ == "__main__":
    main()
